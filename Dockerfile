FROM python:3.7-stretch
ENV PYTHONUNBUFFERED 1

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update \
	&& apt-get install -y postgresql-client-11 binutils libproj-dev gdal-bin

RUN pip install -U pip

RUN mkdir /code
WORKDIR /code

# Install the python dependencies that this project uses:
COPY requirements /code/requirements
RUN pip install -r requirements/dev.txt
RUN pip install -r requirements/deploy.txt

# Install the specific version of node that this project uses:
RUN mkdir /usr/local/nvm
ENV NVM_DIR /usr/local/nvm
RUN wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
RUN . $NVM_DIR/nvm.sh && nvm install 10 && nvm alias default 10
RUN (echo '. $NVM_DIR/nvm.sh' ; echo 'nvm use default') >> /root/.profile

COPY . /code/
RUN . $NVM_DIR/nvm.sh && nvm use && npm install