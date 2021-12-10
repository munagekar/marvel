FROM python:3.8-slim

# Copy python packages from previous stage
COPY requirements.txt requirements.txt
RUN pip install --no-cache -r requirements.txt

WORKDIR /project

COPY webhook webhook