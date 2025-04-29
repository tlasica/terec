# Build stage
FROM python:3.12-slim as builder

ARG wheel=terec_api-0.1.0-py3-none-any.whl

WORKDIR /build

# Install build dependencies
RUN python -m pip install --upgrade pip && \
    pip install uv

# Copy and install the wheel
COPY ./dist/$wheel /build/$wheel
RUN uv pip install --system --no-cache-dir --upgrade /build/$wheel

# Copy configuration
COPY ./log_conf.yaml /build/log_conf.yaml

# Final stage
FROM python:3.12-slim

WORKDIR /code

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /build/log_conf.yaml /code/log_conf.yaml

CMD ["uvicorn", "terec.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_conf.yaml"]
