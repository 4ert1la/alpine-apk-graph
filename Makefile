PYTHON := python3

.PHONY: test demo clean

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) -m src.main --package A --repo tests/data/simple.txt --test-mode --output demo.svg

clean:
	rm -f graph.svg graph.puml demo.svg demo.puml
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
