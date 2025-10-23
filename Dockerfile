FROM python:3.9-slim

# Set working directory inside container (project root, not api/)
WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire project into the container
COPY . /code

# Railway sets $PORT automatically, fallback to 8000 for local runs
ENV PORT=8000
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["sh", "-c", "python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT} --reload"]
