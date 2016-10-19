# base conda with scipy stack
FROM jupyter/scipy-notebook

# change user from jovyan - jupyter default
USER root

# additional setup
RUN apt-get update -y && apt-get upgrade -y

# python setup
RUN apt-get install -y libpq-dev python-dev

# revert user
USER $NB_USER

# add requirements
ADD requirements.txt /requirements.txt

# run pip installation
RUN pip install --upgrade -r /requirements.txt

# set working directory
WORKDIR /App

# we don't need to expose ports
