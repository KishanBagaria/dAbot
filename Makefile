all: clean build

clean:
	rm -rf dist/ build/ *.egg-info
build:
	python2 setup.py sdist bdist_wheel

upload-test:
	twine upload -r pypitest dist/*
register-test:
	twine register -r pypitest dist/*.tar.gz
upload:
	twine upload dist/*
register:
	twine register dist/*.tar.gz
