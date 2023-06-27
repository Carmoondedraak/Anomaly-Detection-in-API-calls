FROM python:3.8.7-slim-buster

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

ENV FLASK_APP main
ENV FLASK_ENV development

RUN pip3 install pipenv && pipenv install --deploy && pipenv install connexion[swagger-ui]

ENTRYPOINT ["/usr/local/bin/pipenv", "run", "python3", "main.py"]

