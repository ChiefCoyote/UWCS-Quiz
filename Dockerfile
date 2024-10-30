FROM python:3.12
RUN pip install pipenv
WORKDIR /app
COPY . .
RUN pipenv install --system -r requirements.txt
CMD gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:8080 main:app