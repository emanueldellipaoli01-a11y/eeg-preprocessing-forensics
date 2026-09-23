# Contributing

New cases should compare two preprocessing choices using the same data and the same downstream analysis.

For a new case:

1. define the preprocessing choice being compared;
2. document variants A and B;
3. keep the other analysis settings fixed;
4. record the dataset, version, and source;
5. define the primary metric before running the comparison;
6. save the numerical results and relevant figures;
7. document limitations and the scope of the result;
8. add tests for new code or metadata.

Before opening a pull request, run:

```bash
python -m pytest -q
ruff check .
python tools/validate_registry.py
```

A case should not present a single-subject result as evidence for a broader population.

Please keep the code for a new case inside its case directory unless there is a clear reason to share it with other cases.
