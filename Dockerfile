FROM python:3.9-slim

# Set working dir inside container
WORKDIR /code/app

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the api code into the container
COPY ./app /code/app

# Railway sets $PORT automatically, fallback to 8000 for local runs
ENV PORT=8000
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
