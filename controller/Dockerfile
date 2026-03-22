FROM python:3.11-slim

WORKDIR /app
COPY api.py .
COPY static ./static

RUN pip install fastapi "uvicorn[standard]"

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]