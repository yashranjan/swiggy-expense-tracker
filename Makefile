gen_data:
	python3 swiggy.py

update_dep:
	pip freeze > requirements.txt