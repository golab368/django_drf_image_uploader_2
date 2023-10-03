# # Django-DRF-IMAGE-UPLOADER

# General info

Django DRF project based on creating thumbnail of uploaded images e.g. .png .jpg

An Admin can create accounts types and assign them the capability to generate thumbnails for example in the following forms:

User Profile with account type Enterprise are able to: upload images and get thumbnail 200x200 and 400x400 also they can set expiration time.

User Profile with account type Premium are able to: upload images and get thumbnail 200x200 and 400x400.

User Profile with account type Basic are able to: upload images and get thumbnail 200x200.




# Coverage 94%

![screenshot](https://i.imgur.com/ur8OLf4.png)

# Technologies
- Django DRF
- Redis
- Celery

# Setup

1. Clone the Repository: django_drf_image_uploader_2

```git clone [URL-of-the-GitHub-repository]
cd [django_drf_image_uploader_2]
```

2. Setup a Virtual Environment:

```python3 -m venv venv
source venv_name/bin/activate  # Activates the virtual environment
```
3. Install Dependencies:

```
pip install -r requirements.txt
```

4. Database and APP Setup:

```Pay attention on .env check .env.examples```

```- python or python3 manage.py makemigrations api
- python or python3 manage.py migrate
- python or python3 manage.py createsuperuser
- python manage.py createsuperuser
- python manage.py changepassword e.g. admin
```

# Setup on Docker

```
docker build -t api .
docker run -p 8000:8000 api_images
#Check the container number by CONTAINER ID:
docker exec -it YOUR_CONTAINER_ID python manage.py makemigrations api
docker exec -it YOUR_CONTAINER_ID python manage.py migrate
docker exec -it YOUR_CONTAINER_ID python manage.py createsuperuser
docker exec -it YOUR_CONTAINER_ID python manage.py changepassword e.g. admin
```


# how to use:
1. http://127.0.0.1:8000/admin
2. http://127.0.0.1:8000/login
3. http://127.0.0.1:8000/create
4. http://127.0.0.1:8000/images

