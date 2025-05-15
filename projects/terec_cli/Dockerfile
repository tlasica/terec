FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV TEREC_URL http://localhost:8000

ARG wheel=terec_cli-0.1.0-py3-none-any.whl

WORKDIR /code

COPY ./dist/$wheel /code/$wheel

RUN uv pip install --system --no-cache-dir --upgrade /code/$wheel

## Define an entry-point script to direct commands to the correct main.py
COPY entrypoint.sh /usr/local/bin/terec
RUN chmod +x /usr/local/bin/terec
