# Use the official Python base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
RUN apt-get update && \
    apt-get install -y ssdeep
    
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application into the container
COPY . .

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Run the command to start the application
CMD ["python", "entry_script.py"]
