FROM python:3.13-slim

# Set working directory
WORKDIR /code

# Copy code and install dependencies
COPY backend/ ./backend/
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r backend/requirements.txt


# Set Python path so 'backend' is importable
ENV PYTHONPATH=/code

# Railway sets $PORT automatically, fallback to 8000 for local runs
ENV PORT=8000
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT} --reload"]