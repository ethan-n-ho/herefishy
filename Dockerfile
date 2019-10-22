FROM python:3.6

ARG PIP_REQUIRES=/home/requirements.txt

# apt-get installs
RUN apt-get update

# pip installs
COPY requirements.txt $PIP_REQUIRES
RUN pip install -r $PIP_REQUIRES
