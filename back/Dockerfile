FROM python:3.7-slim-buster

WORKDIR /app
RUN apt update && apt install libglib2.0-0 libgl1-mesa-glx libsm6 libxext6 -y 
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

COPY . .

CMD [ "python3", "main.py"]