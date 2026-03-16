# Use a slim Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system tools needed for compiling C++ libraries (like ChromaDB)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first (for Docker caching)
COPY requirements.txt .

# 🔥 CRITICAL FIX: Upgrade pip first so it can solve complex dependencies
RUN pip install --upgrade pip

# Install the Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 CRITICAL: Install Playwright and its hidden OS dependencies
RUN playwright install --with-deps chromium

# Copy the rest of your backend code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the server with hot-reloading
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]