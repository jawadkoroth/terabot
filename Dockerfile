FROM python:3.9-slim

# Install necessary system dependencies (compilers, SSL, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools to the latest versions
RUN pip install --upgrade pip setuptools

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Display versions for debugging
RUN python --version
RUN pip --version

# Install the Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the bot
CMD ["python", "bot.py"]
