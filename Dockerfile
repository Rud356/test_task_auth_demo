FROM python:3.13-slim-bookworm
LABEL authors="Rud356"

WORKDIR /app
COPY . /app

RUN python -m venv .env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
RUN pip install --no-cache-dir -e .[migration]

CMD ["python", "-m", "src.demo_api"]