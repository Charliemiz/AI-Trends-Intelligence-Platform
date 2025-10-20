FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependencies first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port (Railway sets $PORT automatically)
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main", "--host", "0.0.0.0", "--port", "8000"]