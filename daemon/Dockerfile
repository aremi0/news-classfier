FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN mkdir /app/dataframe

COPY . .

CMD ["python3", "./nonRTDaemon.py"]

# docker build . --tag tap:daemon