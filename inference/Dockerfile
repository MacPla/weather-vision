
FROM python:3.9-slim

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 ffmpeg

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "predict.py"]
