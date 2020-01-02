FROM python:3.6.9
ADD . /app
WORKDIR /app
EXPOSE 5000
CMD ["gunicorn", "--workers", "3", "--threads", "2", "--bind", "0.0.0.0:5000", "manage:app"]
