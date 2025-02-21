FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-chace-dir -r requirements.txt

COPY . .

# Expose the Flask port
EXPOSE 5000

CMD ["python", "main.py"]