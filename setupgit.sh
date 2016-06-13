#!/usr/bin/env bash
git config --global user.email "dtsai@skymizer.com"
git config --global user.name "Daniel Tsai"
git config --global core.editor vim

aptitude update
aptitude upgrade -y
aptitude install -y python3-pip libpng12-dev libexpat1-dev ocaml-findlib libfindlib-ocaml-dev ocaml
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 100
update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.9 100
pip3 install --allow-all-external mysql-connector-python
