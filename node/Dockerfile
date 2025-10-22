# node/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install the C compiler and other build tools first
RUN apt-get update && apt-get install -y build-essential

# Now, copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

CMD ["python", "app.py"]