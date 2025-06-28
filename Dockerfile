# Use an official Python runtime as a parent image.
# The python:3.11-slim image is multi-platform and supports linux/arm64.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
# Using --no-cache-dir to keep the image size down
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY bot.py .

# The bot loads credentials from environment variables.
# These should be passed in at runtime, not baked into the image.
# e.g., using `docker run --env-file .env ...`

# Command to run the application
CMD ["python", "bot.py"]
