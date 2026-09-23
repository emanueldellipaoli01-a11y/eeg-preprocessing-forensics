# Case 001 — High-pass 0.1 Hz vs 1 Hz

## Question

How much does changing the continuous-EEG high-pass cutoff from 0.1 Hz to 1.0 Hz change a response-locked ERN amplitude estimate in the ERP CORE Flankers task?

## Data

ERP CORE v1.1.1, Flankers task.

* Dataset: NEMAR nm000132
* DOI: 10.82901/nemar.nm000132
* License: CC-BY-4.0
* Subject: 001
* Raw-file SHA-256: recorded in `results/manifest.json`

The empirical run used the official MNE ERP CORE fetcher.

Raw EEG files are not stored in this repository.

## Pipelines

The two pipelines differ only in the high-pass cutoff.

| Setting        |          Variant A |       Variant B |
| -------------- | -----------------: | --------------: |
| High-pass      |             0.1 Hz |          1.0 Hz |
| Low-pass       |              40 Hz |           40 Hz |
| Filter         |    FIR, zero phase | FIR, zero phase |
| Reference      |            average |         average |
| Epoch          |      −0.5 to 1.0 s |            same |
| Baseline       |     −0.5 to −0.2 s |            same |
| Rejection      |             150 µV |            same |
| Event          | incorrect response |            same |
| Sensor         |                FCz |            same |
| Scoring window |           0–100 ms |            same |

## Analysis

For each variant the analysis:

1. loads the same recording;
2. applies the selected high-pass filter and the common low-pass filter;
3. applies the average reference;
4. extracts incorrect-response epochs;
5. applies the same baseline and rejection rule;
6. averages the epochs;
7. computes the mean FCz voltage from 0 to 100 ms after the response.

No stochastic method is used.

The 0–100 ms window is the scoring window used for this case.

## Result

Subject 001 produced:

| High-pass | Mean FCz amplitude | Accepted epochs |
| --------- | -----------------: | --------------: |
| 0.1 Hz    |       −6.643538 µV |              34 |
| 1.0 Hz    |       −6.742660 µV |              37 |

The within-subject difference (A − B) was:

```text
0.099122 µV
```

The result is reported for Subject 001 only. No population-level inference is made from this run.

## Figures

* `figures/erp_variant_a_vs_b.png` — variant A and B waveforms
* `figures/erp_difference.png` — A − B waveform
* `figures/subject_level_difference.png` — subject-level difference

## Results files

* `results/manifest.json`
* `results/comparison_table.csv`
* `results/summary_long.csv`

The manifest records the dataset version, input-file hash, source information, software versions, configuration hash, and execution status.

## Limitation

The current public execution contains one subject. The MNE ERP CORE fetcher used for this case provides the Subject 001 recording used here. Additional subjects must be obtained separately before a multi-subject result can be produced.

## Reproduction

With the MNE fetcher:

```bash
python -m cases.case_001_highpass_01_vs_1hz.run --subjects 1
```

With a local recording:

```bash
python -m cases.case_001_highpass_01_vs_1hz.run   --raw-path /path/to/ERP-CORE_Subject-001_Task-Flankers_eeg.fif
```

For several subjects:

```bash
python -m cases.case_001_highpass_01_vs_1hz.run   --subjects 1 2 3 4 5
```

## References

1. Acunzo, D., Mackenzie, I. G., & van Rossum, M. C. W. (2012). Systematic biases in early ERP and ERF components as a result of high-pass filtering. *Journal of Neuroscience Methods, 209*(1), 212–218. https://doi.org/10.1016/j.jneumeth.2012.06.011

2. Tanner, D., Morgan-Short, K., & Luck, S. J. (2015). How inappropriate high-pass filters can produce artifactual effects and incorrect conclusions in ERP studies of language and cognition. *Psychophysiology, 52*(8), 997–1009. https://doi.org/10.1111/psyp.12437

3. Zhang, G., & Luck, S. J. (2024). Optimal filters for ERP research I: A general approach for selecting filter settings. *Psychophysiology, 61*(6), e14496. https://doi.org/10.1111/psyp.14496

4. Kappenman, E. S., Farrens, J. L., Zhang, W., Stewart, A. X., & Luck, S. J. (2021). ERP CORE: An open resource for human event-related potential research. *NeuroImage, 225*, 117465. https://doi.org/10.1016/j.neuroimage.2020.117465

5. NEMAR. ERP CORE v1.1.1. https://doi.org/10.82901/nemar.nm000132
