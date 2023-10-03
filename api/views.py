import os
from django.contrib.auth import logout
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .serializers import ImagesSerializer
from django.contrib.auth.views import LoginView
from django.views import View
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Images


class LoginView(LoginView):
    template_name = "login.html"
    success_url = reverse_lazy("api:create")


class LogoutView(RedirectView):
    url = reverse_lazy("api:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class ImagesCreateView(generics.CreateAPIView):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        account_type = self.request.user.userprofile.account_type.name
        if account_type == "None":
            data = {
                "detail": "Your profile hasn't been assigned to any account type. Please contact the admin.",
                "account_type": account_type,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"Account Type": f"Your account is: {account_type}"},
                status=status.HTTP_200_OK,
            )


class UserImagesListView(ListAPIView):
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Images.objects.filter(author=user)


class OriginalFileLink(View):
    def get(self, request, id):
        try:
            image = Images.objects.get(id=id)
        except Images.DoesNotExist:
            raise Http404("Image does not exist")

        # Get the path to the original file
        file_path = os.path.join(settings.MEDIA_ROOT, str(image.image))

        # Check if the file exists
        if not default_storage.exists(file_path):
            raise Http404("Original file does not exist")

        # Get the URL for the original file and return it in the response
        file_url = default_storage.url(file_path)
        return HttpResponse(file_url)
