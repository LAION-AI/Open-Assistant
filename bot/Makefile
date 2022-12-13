install:
	python -m pip install -U pip
	python -m pip install -e .

lint: ## [Local development] Run pylint and black
	python -m pylint app
	python -m black --check -l 120 app

black: ## [Local development] Auto-format python code using black
	python -m black -l 120 .

run:
	python -m bot
