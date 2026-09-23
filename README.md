# EEG Preprocessing Sensitivity

Code and results for controlled comparisons of EEG preprocessing choices.

The idea is simple: keep the data, trials, and downstream analysis fixed and change one preprocessing setting at a time.

The repository currently contains one case.

## Case 001 — High-pass 0.1 Hz vs 1 Hz

The case compares two high-pass filter settings in the ERP CORE Flankers task:

* 0.1 Hz
* 1.0 Hz

The outcome is the mean FCz amplitude from 0 to 100 ms after the response.

The empirical run was performed on ERP CORE Subject 001.

| High-pass          | Mean FCz amplitude |
| ------------------ | -----------------: |
| 0.1 Hz             |         −6.6435 µV |
| 1.0 Hz             |         −6.7427 µV |
| Difference (A − B) |          0.0991 µV |

The result is from one subject only. It is therefore a subject-level observation and does not support a population-level conclusion.

The published outputs are in:

```text
cases/case_001_highpass_01_vs_1hz/
```

The main result files are:

```text
results/manifest.json
results/comparison_table.csv
results/summary_long.csv
```

Figures are in:

```text
figures/
```

## Data

The case uses ERP CORE v1.1.1, Flankers task, accessed through the official MNE ERP CORE fetcher.

The dataset record is:

* NEMAR: nm000132
* DOI: 10.82901/nemar.nm000132
* License: CC-BY-4.0

Raw EEG files are not included in this repository.

The executed raw file is identified by its SHA-256 hash in the case manifest.

## Analysis

The two pipelines are identical except for the high-pass cutoff.

Common settings:

* FIR zero-phase filtering
* low-pass: 40 Hz
* average reference
* response-locked epochs from −0.5 to 1.0 s
* baseline: −0.5 to −0.2 s
* rejection threshold: 150 µV
* incorrect-response epochs
* FCz
* scoring window: 0–100 ms

See the case README and `config.yaml` for the exact settings.

## Reproducing the case

Create an environment and install the package:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

Run the tests:

```bash
python -m pytest -q
```

Run the case with the MNE ERP CORE fetcher:

```bash
python -m cases.case_001_highpass_01_vs_1hz.run --subjects 1
```

A local raw file can also be supplied:

```bash
python -m cases.case_001_highpass_01_vs_1hz.run   --raw-path /path/to/ERP-CORE_Subject-001_Task-Flankers_eeg.fif
```

For multiple subjects, supply the recordings explicitly and list the subjects:

```bash
python -m cases.case_001_highpass_01_vs_1hz.run   --subjects 1 2 3 4 5
```

The current MNE fetcher path used by the case provides the Subject 001 recording; additional subjects must be obtained separately.

## Repository layout

```text
cases/      case-specific analyses and results
src/        small shared utilities
metadata/   case and dataset metadata
tests/      tests and synthetic checks
tools/      small repository utilities
.github/    CI and GitHub templates
```

## Current status

Case 001 has been empirically executed for Subject 001.

The current result should be read as a single-subject sensitivity measurement. Additional subjects are needed before making broader claims.

## References

1. Kappenman, E. S., Farrens, J. L., Zhang, W., Stewart, A. X., & Luck, S. J. (2026). *ERP CORE (Version v1.1.1)* [Data set]. NEMAR. https://doi.org/10.82901/nemar.nm000132

2. Kappenman, E. S., Farrens, J. L., Zhang, W., Stewart, A. X., & Luck, S. J. (2021). ERP CORE: An open resource for human event-related potential research. *NeuroImage, 225*, 117465. https://doi.org/10.1016/j.neuroimage.2020.117465

3. Acunzo, D., Mackenzie, I. G., & van Rossum, M. C. W. (2012). Systematic biases in early ERP and ERF components as a result of high-pass filtering. *Journal of Neuroscience Methods, 209*(1), 212–218. https://doi.org/10.1016/j.jneumeth.2012.06.011

4. Tanner, D., Morgan-Short, K., & Luck, S. J. (2015). How inappropriate high-pass filters can produce artifactual effects and incorrect conclusions in ERP studies of language and cognition. *Psychophysiology, 52*(8), 997–1009. https://doi.org/10.1111/psyp.12437

5. Zhang, G., & Luck, S. J. (2024). Optimal filters for ERP research I: A general approach for selecting filter settings. *Psychophysiology, 61*(6), e14496. https://doi.org/10.1111/psyp.14496

6. MNE-Python documentation: https://mne.tools/stable/
