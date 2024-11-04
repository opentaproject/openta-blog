FROM python:3.11.7-bullseye
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main"  > /etc/apt/sources.list.d/postgresql.list'
RUN apt upgrade -y
RUN apt update -y \
    && apt-get --fix-broken install -y \
    memcached  \
    libmemcached-dev  \
    vim \
    postgresql-14\
    apt-utils \
    redis   \
    supervisor
RUN apt update
RUN mkdir -p /srv/openta-blog
WORKDIR /srv/openta-blog
RUN pip install --upgrade pip
COPY . /srv
RUN pip install -r django/requirements.txt
EXPOSE 8000
