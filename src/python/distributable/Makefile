OPT_CLEAN=--clean
OPT_FORCE=--force
# fixme: probably need a Makefile magic string for .
SOURCE_PATH=.
MAKE_PAPI=${SOURCE_PATH}/free_range/make_papi.py

.PHONY: clean, papi, python_version

papi:
	@echo "Generating Python PAPI from Protobuf API specifications"
	python ${MAKE_PAPI} ${SOURCE_PATH}

clean:
	@echo "Cleaning generated PAPI code"
	python ${MAKE_PAPI} ${SOURCE_PATH} ${OPT_CLEAN}

python_version:
	python --version

# todo: pip target

# todo: test target
