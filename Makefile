PYTHON_SCRIPTS := $(wildcard *.py)
OTHER_SCRIPTS := from_solver to_solver copyHTML.js

OUTPUT_PATH = dist/test_suite.tgz
TAR_ARGS = -czvf ${OUTPUT_PATH}

tarball: ${OUTPUT_PATH}

${OUTPUT_PATH}: ${PYTHON_SCRIPTS} ${OTHER_SCRIPTS}
	@chmod +x $^
	@tar ${TAR_ARGS} $^

.PHONY: clean

clean:
	@rm -rf __pycache__ dist/*
