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
    supervisor \
    npm
RUN apt update
RUN mkdir -p /srv/openta-blog
WORKDIR /srv/openta-blog
RUN pip install --upgrade pip
COPY . /srv
WORKDIR /srv
RUN git clone https://github.com/opentaproject/openta-blog.git -b latest
WORKDIR /srv/openta-blog
RUN pip install -r django/requirements.txt
WORKDIR /srv/openta-blog/django/blog
RUN pip install gunicorn
#RUN npm install --force @tailwindcss/cli 
#RUN npm audit fix
#RUN ["npx","@tailwindcss/cli -i static/css/input.css -o static/css/output.css "]
#RUN python manage.py collectstatic
EXPOSE 8000

