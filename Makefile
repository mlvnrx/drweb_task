PYTHON = python3
WORKDIR = $(shell pwd)

all: create-venv install db run

test: clean all

create-venv:
	$(PYTHON) -m venv venv

venv-activate:
	. $(WORKDIR)/venv/bin/activate

install: venv-activate
	pip3 install -r requirements.txt

run:
	python3 app

clean:
	rm -rf venv .venv

db:
	sqlite3 users.sqlite3 < schema.sqlite3