## Summary

<!-- What does this change and why? Link the issue if there is one. -->

## Validation

<!-- Paste the commands you ran and their result. -->

- [ ] `uv run pytest -m "not network"` passes
- [ ] `uv run pytest -m network` passes (if fields, filters, or markets changed)
- [ ] `uv run python scripts/gen_field_reference.py --check` passes (if the registry changed)
- [ ] `bash scripts/clean_env_smoke.sh` passes (if packaging, dependencies, or CLI changed)

## Compatibility

- [ ] No existing field was renamed or removed
- [ ] `screen_stocks` signature and result shape unchanged (or the change is documented below)
- [ ] New fields: registry + metadata + docstring + docs regenerated + tests
- [ ] Documentation updated (README / docs/) where behavior changed

## Checklist

- [ ] No cookies, tokens, `.env` files, logs with session data, or vendored third-party code
- [ ] Commits are focused and messages describe the change
