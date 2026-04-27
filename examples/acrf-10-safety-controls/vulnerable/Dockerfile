FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.0 requests==2.31.0
COPY safety_api.py /app/
COPY attacker.py /app/
CMD ["python", "-u", "safety_api.py"]
