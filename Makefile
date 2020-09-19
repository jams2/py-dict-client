test:
	nose2 -s tests/ -C --coverage-config .coveragerc && coverage html

dist: test
	pip install -e .[dist]
	rm -f dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/*
