# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory into the container
COPY . .

# Install required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by the bidding microservice
EXPOSE 5002

# Command to run the bidding microservice
CMD ["python", "bidding.py", "amqp_lib.py"]
