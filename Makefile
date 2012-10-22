DEV_STAMP=.dev_env_installed.stamp
VENV_STAMP=.venv_installed.stamp
INSTALL_STAMP=.install.stamp

install: $(INSTALL_STAMP)

install-dev: $(DEV_STAMP)

tests: install-dev
	nosetests --cover-package=respire

$(INSTALL_STAMP): 
	bin/python setup.py develop
	touch $@

$(DEV_STAMP): dev-requirements.txt
	pip install -r dev-requirements.txt
	touch $@
