FROM python:3.13-slim

# Set working directory
WORKDIR /code

# Install dependencies
COPY ./backend/requirements.txt /code/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/backend/requirements.txt

# Copy the entire project into the container
COPY . /code

# Railway sets $PORT automatically, fallback to 8000 for local runs
ENV PYTHONPATH=/code
ENV PORT=8000
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]