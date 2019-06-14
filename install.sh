#!/usr/bin/env bash

rm -rf poster
rm -rf views

mkdir poster
mkdir views
mkdir views/movies
mkdir views/series
mkdir views/episodes

# install virtualenv
# python3 -m venv venv

# abs path
dir=$(pwd)

# var for virtyalenv
venv="$dir/venv/bin"

# install requirements for Python
requirement="$venv/pip install -r requirements.txt"
eval $requirement

# runnig installation
py_install="$venv/python $dir/py_installation.py"
eval $py_install

# running aplication
py_run="$venv/python $dir/mscollection.py"
eval $py_run
