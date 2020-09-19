test:
	nose2 -s tests/ -C --coverage-config .coveragerc && coverage html

build: test
	rm -f dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/*
