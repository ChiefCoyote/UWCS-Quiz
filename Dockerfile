FROM python:3.12
RUN pip install pipenv
WORKDIR /UWCS-Quiz
COPY . /UWCS-Quiz
RUN pipenv install --system
CMD gunicorn --worker-class eventlet -w 1 main:app