FROM python:3.6-onbuild
WORKDIR /usr/src/app
# install docker, rabbitmq, supervisor dependencies
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common rabbitmq-server supervisor
# install docker
RUN curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") $(lsb_release -cs) stable"
RUN apt-get update && apt-get install -y docker-ce
# install docker-compose
RUN curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose
# additional setup for celery
RUN ln -s /run/shm /dev/shm
# celery supervisor setup
COPY codelive-celery.conf /etc/supervisor/conf.d/
RUN service supervisor restart
# start rabbitmq
RUN service rabbitmq-server restart
# additional setup
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]