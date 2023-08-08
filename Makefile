.PHONY: docs

docs: 
	python docs/_scripts/generate_indicator_table.py
	mkdocs gh-deploy