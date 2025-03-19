FROM python:3.12

ARG wheel=terec_api-0.1.0-py3-none-any.whl

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY ./dist/$wheel /code/$wheel
RUN pip install uv
RUN uv pip install --system --no-cache-dir --upgrade /code/$wheel

COPY ./log_conf.yaml /code/log_conf.yaml

CMD ["uvicorn", "terec.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_conf.yaml"]
