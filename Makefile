test:
	nose2 -s tests/ -C --coverage-config .coveragerc && coverage html

build: test
	rm dist/*
	python setup.py bdist sdist_wheel
	twine upload dist/*
