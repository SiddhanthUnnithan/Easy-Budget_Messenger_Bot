# base conda with scipy stack
FROM jupyter/scipy-notebook

# run pip installation
RUN pip install --upgrade -r requirements.txt

# set working directory
WORKDIR /App

# we don't need to expose ports
