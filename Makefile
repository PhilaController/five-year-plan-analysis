# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
ENV_NAME=fyp

create_environment:
	conda create -n $(ENV_NAME) python=3.8 -y
	@echo ">>> New conda env created. Activate with: conda activate $(ENV_NAME)"
	
kedro_install:
	($(CONDA_ACTIVATE) $(ENV_NAME) ; conda install -c conda-forge kedro -y )
	
docs:
	./docs/build_docs.sh "docs"