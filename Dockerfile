FROM python:3.10-slim

# Install Tesseract and OpenCV dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "8000"]

RUN python -c "import nltk; nltk.download('punkt', download_dir='./nltk_data')"
