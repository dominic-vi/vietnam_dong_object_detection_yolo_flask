FROM python:3.8

WORKDIR /usr/src/app

COPY . .

RUN apt-get update && apt-get install -y libglib2.0-0 libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "app.py"]