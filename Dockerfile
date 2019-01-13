FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
  # for database access:
  postgresql-client-9.6 \
  gettext \
  libgettextpo-dev

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
RUN wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
RUN . $NVM_DIR/nvm.sh && nvm install 8 && nvm alias default 8
RUN (echo '. $NVM_DIR/nvm.sh' ; echo 'nvm use default') >> /root/.profile

# Add all code and node_modules for CirclCI to have access:
COPY . /code/
RUN . $NVM_DIR/nvm.sh && nvm use && npm install
