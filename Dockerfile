# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies including tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# Set the working directory in the container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "8000"]
