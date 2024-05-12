FROM python:3
WORKDIR /workspace/ellipsis
RUN apt-get -y install git
RUN python -m pip install --upgrade pip wheel setuptools
COPY . .
RUN python -m pip install ".[dev]"
