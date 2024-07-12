# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY automation.py .
COPY pdf_creator.py .


# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the Python script
ENTRYPOINT ["python", "automation.py"]


#docker build -t carbon_automation .
#carbon run --rm -v file_path_of_csv_files:/data carbon_automation /data
