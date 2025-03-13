FROM python:3.9-slim

WORKDIR /myapp

COPY require.txt .

RUN pip install --no-cache-dir -r require.txt

COPY . .

CMD ["python", "main.py"]