PYTHON_SCRIPTS := $(wildcard *.py)
BASH_SCRIPTS := from_solver to_solver

OUTPUT_PATH = dist/test_suite.tgz
TAR_ARGS = -czvf ${OUTPUT_PATH}

tarball: ${OUTPUT_PATH}

${OUTPUT_PATH}: ${PYTHON_SCRIPTS} ${BASH_SCRIPTS}
	tar ${TAR_ARGS} $^

.PHONY: clean

clean:
	@rm -rf __pycache__ dist/*
