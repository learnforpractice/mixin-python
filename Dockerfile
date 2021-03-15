FROM rocker/binder:3.6.3

## Declares build arguments
ARG NB_USER
ARG NB_UID

## Copies your repo files into the Docker Container
USER root
RUN python3 --version
## Install eosio.cdt 1.7.0
RUN apt update
RUN apt install -y libncurses5

COPY . ${HOME}
## Enable this to copy files from the binder subdirectory
## to the home, overriding any existing files.
## Useful to create a setup on binder that is different from a
## clone of your repository
## COPY binder ${HOME}
RUN chown -R ${NB_USER} ${HOME}

## Become normal user again
USER ${NB_USER}

## Run an install.R script, if it exists.
RUN if [ -f install.R ]; then R --quiet -f install.R; fi
RUN python3 -m pip install https://github.com/learnforpractice/mixin-python/releases/download/v0.1/mixin-0.1.0-cp37-cp37m-linux_x86_64.whl
