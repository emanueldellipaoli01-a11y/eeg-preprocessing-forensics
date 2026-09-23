## Summary

What changed?

## Case checks

- [ ] Only the intended preprocessing choice changes.
- [ ] Dataset and version are documented.
- [ ] Variant A and B use the same downstream analysis.
- [ ] Results and figures are included where needed.
- [ ] Limitations are documented.

## Verification

- [ ] `python -m pytest -q`
- [ ] `ruff check .`
- [ ] `python tools/validate_registry.py`
