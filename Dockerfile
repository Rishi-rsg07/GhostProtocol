# Use a lightweight Python base image
FROM python:3.10-slim

# Install system dependencies required for OpenCV and video handling
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set up project workspace
WORKDIR /app

# Install Python requirements
COPY requirements_edge.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and the optimized model
COPY src/ ./src
COPY models/ ./models
COPY main.py .

# Environment flag to let OpenCV run without a physical monitor (headless mode)
ENV DISPLAY=:0

# Execute pipeline on container startup
CMD ["python", "main.py"]