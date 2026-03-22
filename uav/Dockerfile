FROM python:3.11-slim

WORKDIR /app

COPY uav.py .
COPY main.py .
COPY utility.py .
COPY uav_specs.json .
COPY edge_specs.json .

RUN pip install requests

CMD ["python", "main.py"]