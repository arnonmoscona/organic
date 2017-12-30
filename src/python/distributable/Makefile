OPT_CLEAN=--clean
OPT_FORCE=--force
SOURCE_PATH=.
MAKE_PAPI=free_range/make_papi.py

.PHONY: papi

papi: $(PAPIS2)
	@echo "Generating Python PAPI from Protobuf API specifications"
	python ${MAKE_PAPI} ${SOURCE_PATH}

python_version:
	python --version
