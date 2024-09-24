FROM python:3.8

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "app.py"]