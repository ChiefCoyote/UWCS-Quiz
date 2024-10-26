FROM python:3.12
RUN pip install pipenv
WORKDIR /UWCS-Quiz
COPY . /UWCS-Quiz
RUN pipenv install --system
CMD gunicorn main:main -b 0.0.0.0:8080