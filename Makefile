VENV = venv
VENV_PYTHON    = $(VENV)/bin/python
SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
# If virtualenv exists, use it. If not, find python using PATH
#PYTHON         = $(or $(wildcard $(VENV_PYTHON)), $(SYSTEM_PYTHON))
PYTHON         = $(VENV_PYTHON)
PIP            = $(dir $(PYTHON))pip

PKG_NAME = $(shell grep -A 1 '\[project\]' pyproject.toml | grep 'name' | sed 's/.*=\s*//' | sed 's/"//g')
MOD_NAME = $(shell echo $(PKG_NAME)| sed 's/-/_/g')

.PHONY: clean deps deps-dev dev dist lint pkg-name test venv debug systemd-install systemd-remove
.SILENT: pkg-name


default: dist

deps: venv
	$(PIP) install -r requirements.txt

deps-dev: deps
	$(PIP) install -r requirements-dev.txt

dist: venv deps deps-dev
	$(PIP) install build
	$(PYTHON) -m build --sdist
	$(PYTHON) -m build --wheel

etc-config:
	sudo mkdir -p /etc/$(PKG_NAME)
	sudo cp etc/config.ini /etc/$(PKG_NAME)/config.ini

lint: venv
	$(PYTHON) -m flake8 $(MOD_NAME)

dev: pkg-name venv deps deps-dev
	$(PIP) show $(PKG_NAME) > /dev/null || $(PIP) install -e .

pkg-name:
	if [ -z "$(PKG_NAME)" ]; then \
		echo "Project name could not be found. Please make sure the 'name' field is the first line within the [project] section of your pyproject.toml"; \
		exit 1; \
	else \
		echo "Project name is: '$(PKG_NAME)'"; \
	fi

# Dev/build environment
$(VENV_PYTHON):
	$(SYSTEM_PYTHON) -m venv $(VENV)

venv: $(VENV_PYTHON)

systemd-install:
	sudo cp systemd/$(PKG_NAME).service /etc/systemd/system
	sudo systemctl daemon-reload

systemd-remove:
	sudo systemctl stop $(PKG_NAME).service
	sudo rm /etc/systemd/system/$(PKG_NAME).service
	sudo systemctl daemon-reload

clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
	rm -rf src/*.egg-info
	rm -rf dist
	rm -rf $(VENV)
