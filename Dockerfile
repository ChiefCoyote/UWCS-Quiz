FROM python:3.12
RUN pip install pipenv
WORKDIR /app
COPY . .
RUN pipenv install --system
CMD gunicorn --worker-class eventlet -w 1 main:app