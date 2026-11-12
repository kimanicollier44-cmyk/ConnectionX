FROM python:3.12-slim
WORKDIR /app
COPY connectionx/ ./connectionx/
COPY main.py checks.py ./
RUN python checks.py
CMD ["python", "main.py", "demo"]
