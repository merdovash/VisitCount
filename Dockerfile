FROM python:3.6-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install

FROM base
COPY --from=builder /install /usr/local

COPY . /app
WORKDIR /app
RUN pip install -r server_requirements.txt
CMD ["gunicorn", "-w 4", "main:app"]