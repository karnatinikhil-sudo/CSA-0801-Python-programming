FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app/

# Expose port for Django web app
EXPOSE 8000

# Run migrations, load tips, and start development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata fixtures/wellness_tips.json && python manage.py runserver 0.0.0.0:8000"]
