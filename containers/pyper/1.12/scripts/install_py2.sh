#!/bin/sh
	set -e
        export DEBIAN_FRONTEND=noninteractive
	apt update && apt install -y python2-dev libpython2-dev
	curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
	python2 get-pip.py
	python2 -m pip --no-cache-dir install --upgrade pip setuptools
	pip2 install -r /opt/scripts/requirements_py2.txt
	pip2 install --upgrade awscli --ignore-installed six
