# Use a slim Python image as a base
FROM python:3.12-slim

# Set a working directory
WORKDIR /app

# Copy all necessary files
COPY . /app

# Install dependencies
RUN pip install poetry && poetry install --no-dev

# Define an entry-point script to direct commands to the correct main.py
COPY entrypoint.sh /usr/local/bin/terec
RUN chmod +x /usr/local/bin/terec

ENTRYPOINT ["terec"]
