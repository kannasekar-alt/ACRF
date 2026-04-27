FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask==3.0.0 requests==2.31.0
COPY registry.py /app/
COPY malicious_skill.py /app/
COPY agent.py /app/
CMD ["python", "-u", "agent.py"]
