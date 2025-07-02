# Stage 1: Build the virtual environment
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Create a virtual environment
RUN python -m venv /app/venv

# Activate the virtual environment and install dependencies
COPY requirements.txt .
RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Stage 2: Create the final image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/venv ./venv

# Copy the application code
COPY bot.py .

# The bot loads credentials from environment variables.
# These should be passed in at runtime, not baked into the image.
# e.g., using `docker run --env-file .env ...`

# Command to run the application using the python from the venv
CMD ["/app/venv/bin/python", "bot.py"]