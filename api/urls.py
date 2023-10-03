from django.urls import path
from .views import (
    ImagesCreateView,
    LoginView,
    LogoutView,
    UserImagesListView,
    OriginalFileLink,
)

app_name = "api"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create/", ImagesCreateView.as_view(), name="create"),
    path(
        "images/",
        UserImagesListView.as_view(),
        name="user_images_list",
    ),
    path("images/<int:id>/original/", OriginalFileLink.as_view(), name="original_file"),
]
