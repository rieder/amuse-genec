#!/usr/bin/env sh
git clone https://github.com/rieder/amuse.git amuse-genec
cd amuse-genec
git checkout add_genec
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r recommended.txt
./configure
pip install -e .
make framework
cd src/amuse/community/genec
mkdir src
cd src
git clone git@github.com:GESEG/GENEC.git
cd GENEC
git checkout feature/amuse
cd ../..
make
