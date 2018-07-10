#!/bin/bash

VENV_ROOT=/home/wingz/virtualenvs
VENV_NAME=$1
VENV_PATH=$VENV_ROOT/$VENV_NAME
if [ ! -d $VENV_PATH ]; then
	echo "The $VENV_NAME virtualenv doesn't exist. It will be created."
	virtualenv -p python3 $VENV_PATH
fi
# pip install -r requirements.txt
