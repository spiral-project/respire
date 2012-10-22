DEV_STAMP=.dev_env_installed.stamp
INSTALL_STAMP=.install.stamp

install: $(INSTALL_STAMP)

install-dev: $(DEV_STAMP)

tests: install-dev
	# Run todo server
	serve_todo & echo $$! > /tmp/daemon.pid
	sleep 1
	-nosetests --cover-package=respire
	# Kill todo_server
	kill `cat /tmp/daemon.pid`; rm /tmp/daemon.pid

$(INSTALL_STAMP): setup.py setup.cfg
	bin/python setup.py develop
	touch $@

$(DEV_STAMP): dev-requirements.txt
	pip install -r dev-requirements.txt
	touch $@
