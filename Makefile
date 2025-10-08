.PHONY: md-lint md-fix

md-lint:
	uv run pymarkdown --config .pymarkdown.toml scan .

md-fix:
	uv run pymarkdown --config .pymarkdown.toml fix .

# Optional future experiment:
# md-lint-rust:
# 	# Example: uv run mado check .
