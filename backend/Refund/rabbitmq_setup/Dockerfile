FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Forcefully remove and replace any existing amqp_setup.py before copying
RUN rm -f amqp_setup.py

# Copy the rest of the application, including amqp_setup.py and other files
COPY . .

# Run the application
CMD ["python", "amqp_setup.py"]