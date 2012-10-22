DEV_STAMP=.dev_env_installed.stamp
VENV_STAMP=.venv_installed.stamp
INSTALL_STAMP=.install.stamp

install: $(INSTALL_STAMP)
	python setup.py develop

install-dev: $(DEV_STAMP)
	pip install -r dev-requirements.txt

tests: install-dev
	nosetests --cover-package=respire

%.stamp:
	touch $@
