FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY async_scrape.py .
CMD ["python", "async_scrape.py"]
