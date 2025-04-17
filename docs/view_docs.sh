#!/bin/sh

$(sphinx-apidoc -f --module-first --no-toc -o . ../src/ && make clean && make html && cd _build/html && python -m http.server)
