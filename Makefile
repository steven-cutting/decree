.PHONY: md-lint md-fix

md-lint:
uv run pymarkdown scan .

md-fix:
uv run pymarkdown fix .

# Optional future experiment:
# md-lint-rust:
# 	# Example: uv run mado check .
