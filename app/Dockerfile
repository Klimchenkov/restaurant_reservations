FROM python:3.10.5
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./app/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt --no-cache-dir

COPY ./app/src /app

EXPOSE 5000

CMD ["python", "app.py"]