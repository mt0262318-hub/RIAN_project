FROM python:3.10-slim

RUN apt-get update && apt-get install -y xvfb x11-utils python3-tk scrot && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]