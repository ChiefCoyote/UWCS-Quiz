FROM python:3.12
RUN pip install pipenv
WORKDIR /UWCS-Quiz
COPY . .
RUN pipenv install --system
CMD gunicorn app:main -b 0.0.0.0:8080