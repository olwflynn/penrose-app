# syntax=docker/dockerfile:1
FROM python:3.9-alpine
WORKDIR /app
ENV FLASK_APP=src.main.app.py
ENV DEBUG=True
ENV FLASK_ENV=development
CMD echo "flask-app-path = $FLASK_APP"
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]