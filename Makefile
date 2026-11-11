.PHONY: setup preflight demo test evaluate semantic serve
setup:
	uv sync --frozen
preflight:
	uv run runbookops preflight
demo:
	uv run runbookops demo
test:
	uv run pytest -q
evaluate:
	uv run runbookops evaluate
semantic:
	uv run runbookops --embedding semantic index
serve:
	uv run runbookops serve
