# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files from the current directory to the container's /app directory
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the bot (replace bot.py with your bot file name)
CMD ["python", "bot.py"]
