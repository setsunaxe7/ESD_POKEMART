# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory into the container
COPY . .

# Install required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by the inventory microservice
EXPOSE 5006

# Command to run the inventory microservice
CMD ["python", "external_grading.py"]
