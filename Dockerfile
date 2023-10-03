# Use the specified Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install necessary system packages and Python dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container
COPY . .

# Run migrations and collect static files
# Consider running these as part of your deployment process instead of during the build
RUN python manage.py migrate --noinput && python manage.py collectstatic --noinput

# Copy the start script (if you have one) into the container
COPY start.sh .

# If you have a start script, make it executable
RUN chmod +x start.sh

# Specify the command to run on container start
CMD ["./start.sh"]
