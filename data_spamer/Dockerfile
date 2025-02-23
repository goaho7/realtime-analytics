FROM python:3.12

WORKDIR /data_spamer

COPY . .

RUN pip install --upgrade pip
RUN pip install requests

CMD ["python", "main.py"]
