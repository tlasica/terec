# Use a slim Python image as a base
FROM python:3.12-slim

ENV TEREC_URL http://localhost:8000

ARG wheel=terec_cli-0.1.0-py3-none-any.whl

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY ./dist/$wheel /code/$wheel
RUN pip install uv
RUN uv pip install --system --no-cache-dir --upgrade /code/$wheel

## Set a working directory
#WORKDIR /app
#
## Copy all necessary files
#COPY . /app
#
## Install dependencies
#RUN pip install poetry && poetry install
#
## Define an entry-point script to direct commands to the correct main.py
COPY entrypoint.sh /usr/local/bin/terec
RUN chmod +x /usr/local/bin/terec

# ENTRYPOINT ["terec"]
