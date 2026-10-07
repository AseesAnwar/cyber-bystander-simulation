# Assessment Task 2 Draft

This draft gives you:

- SAS code skeletons for each question
- the key numerical results I computed from the CSV files
- short interpretation text you can adapt into your own submission

You still need to run the SAS code and paste the actual SAS output into your final report, because the task explicitly asks for SAS code and SAS output.

## Question 1: WBC

### Import

```sas
proc import datafile="/Users/aseesanwar/Downloads/Dataset WBC.csv"
    out=wbc
    dbms=csv
    replace;
    guessingrows=max;
run;
```

### A(a): Group mean vectors, covariance matrices, correlation matrices

```sas
proc sort data=wbc; by Status; run;

proc means data=wbc mean std;
    class Status;
    var Eccentricity Area Perimeter Solidity Extent Diameter;
run;

proc corr data=wbc cov;
    by Status;
    var Eccentricity Area Perimeter Solidity Extent Diameter;
run;
```

Computed mean vectors:

- Diseased: `[-0.0900, 0.0180, -0.0480, -0.0300, -0.1360, 0.0380]` is the difference vector `(Diseased - Non-diseased)`.
- Diseased mean vector: `[214.9240, 129.9520, 129.6960, 8.2900, 10.1000, 141.5360]`
- Non-diseased mean vector: `[215.0140, 129.9340, 129.7440, 8.3200, 10.2360, 141.4980]`

Strongest sample correlations in both groups:

- Most negative: `Solidity` and `Extent`
- Most positive: `Area` and `Perimeter`

### A(b)-(d): Two-sample Hotelling's T-squared test

Hypotheses:

- `H0: mu_D = mu_ND`
- `H1: mu_D != mu_ND`

Test statistic:

```text
T2 = (n1*n2/(n1+n2)) (xbar1 - xbar2)' Sp^{-1} (xbar1 - xbar2)

Sp = ((n1-1)S1 + (n2-1)S2) / (n1+n2-2)

F = ((n1+n2-p-1)/((n1+n2-2)p)) T2 ~ F_{p, n1+n2-p-1}
```

SAS:

```sas
proc glm data=wbc;
    class Status;
    model Eccentricity Area Perimeter Solidity Extent Diameter = Status;
    manova h=Status / printh printe;
run;
quit;
```

Computed result:

- `T2 = 6.0116`
- `F = 0.9508`
- `df = (6, 93)`
- `p = 0.4630`

Interpretation:

At the 5% level, we fail to reject `H0`. There is no statistically significant multivariate difference between the diseased and non-diseased WBC mean vectors.

Assumptions to discuss:

- independent random samples
- approximate multivariate normality within each group
- common covariance matrices if using the pooled Hotelling test
- no serious multivariate outliers

### A(e): Which variables differ individually?

Use pooled-variance two-sample t tests.

```sas
proc ttest data=wbc;
    class Status;
    var Eccentricity Area Perimeter Solidity Extent Diameter;
run;
```

Computed pooled tests:

| Variable | Difference `(D-ND)` | t | p-value |
|---|---:|---:|---:|
| Eccentricity | -0.0900 | -1.1630 | 0.2476 |
| Area | 0.0180 | 0.2460 | 0.8062 |
| Perimeter | -0.0480 | -0.6736 | 0.5022 |
| Solidity | -0.0300 | -0.2322 | 0.8168 |
| Extent | -0.1360 | -1.0483 | 0.2971 |
| Diameter | 0.0380 | 0.4233 | 0.6730 |

Interpretation:

No individual WBC variable is significant at the 5% level.

### A(f): 95% simultaneous confidence intervals

Formula:

```text
(xbar1_i - xbar2_i) +- sqrt(c * Sp(ii) * (1/n1 + 1/n2))

c = ((n1+n2-2)p/(n1+n2-p-1)) F_{alpha; p, n1+n2-p-1}
```

Computed 95% simultaneous CIs:

| Variable | Lower | Upper |
|---|---:|---:|
| Eccentricity | -0.3785 | 0.1985 |
| Area | -0.2547 | 0.2907 |
| Perimeter | -0.3136 | 0.2176 |
| Solidity | -0.5115 | 0.4515 |
| Extent | -0.6196 | 0.3476 |
| Diameter | -0.2966 | 0.3726 |

### A(g): 95% Bonferroni confidence intervals

Formula:

```text
(xbar1_i - xbar2_i) +- t_{1-alpha/(2p), n1+n2-2} sqrt(Sp(ii)(1/n1 + 1/n2))
```

Computed 95% Bonferroni CIs:

| Variable | Lower | Upper |
|---|---:|---:|
| Eccentricity | -0.2984 | 0.1184 |
| Area | -0.1790 | 0.2150 |
| Perimeter | -0.2399 | 0.1439 |
| Solidity | -0.3779 | 0.3179 |
| Extent | -0.4854 | 0.2134 |
| Diameter | -0.2037 | 0.2797 |

### A(h): Conclusion from the intervals

Every simultaneous CI and every Bonferroni CI contains 0, so none of the six WBC characteristics differs significantly between the two groups.

### B(a): 90% prediction ellipses for strongest positive and negative pairs

The same two pairs appear in both groups:

- strongest positive: `Area` and `Perimeter`
- strongest negative: `Solidity` and `Extent`

```sas
proc corr data=wbc plots=matrix(histogram ellipse=prediction(alpha=0.10));
    by Status;
    var Area Perimeter Solidity Extent;
run;
```

### B(b): Multivariate normality

For a SAS-friendly submission, you can use Q-Q plots and marginal diagnostics:

```sas
proc univariate data=wbc normal;
    by Status;
    var Eccentricity Area Perimeter Solidity Extent Diameter;
    qqplot;
run;
```

If your lecturer expects a multivariate normality diagnostic, note that Mahalanobis-distance chi-square plots are the stronger multivariate check.

Interpretation from the computed data:

- normality looks questionable, especially because the variables are very discrete and tightly clustered
- diseased group Mardia skewness test gave `p = 0.0040`
- non-diseased group Mardia skewness test gave `p = 0.2348`

So I would write that multivariate normality is at best approximate and should be treated cautiously.

## Question 2: WBC PCA

Run PCA separately for each group using the correlation matrix only.

### Diseased group

```sas
proc princomp data=wbc(where=(Status="Diseased")) cov=0 std plots=all out=d_pca;
    var Eccentricity Area Perimeter Solidity Extent Diameter;
run;
```

Eigenvalues:

- `2.5830, 1.5957, 0.9466, 0.4505, 0.2734, 0.1509`

Proportion explained:

- `0.4305, 0.2659, 0.1578, 0.0751, 0.0456, 0.0252`

Cumulative explained:

- PC1 to PC2: `69.64%`
- PC1 to PC3: `85.42%`

First three principal components from the standardized variables:

```text
PC1 = -0.4542 Z(Eccentricity) -0.5320 Z(Area) -0.5296 Z(Perimeter)
      -0.4138 Z(Solidity) +0.0756 Z(Extent) +0.2308 Z(Diameter)

PC2 = -0.0605 Z(Eccentricity) -0.1795 Z(Area) -0.1415 Z(Perimeter)
      +0.5253 Z(Solidity) -0.7481 Z(Extent) +0.3294 Z(Diameter)

PC3 = +0.4685 Z(Eccentricity) -0.1137 Z(Area) +0.2382 Z(Perimeter)
      -0.1949 Z(Solidity) +0.1616 Z(Extent) +0.8042 Z(Diameter)
```

Pattern-profile interpretation:

- PC1 is mainly an overall size/shape component driven by `Area`, `Perimeter`, `Eccentricity`, and `Solidity`
- PC2 contrasts `Extent` strongly against `Solidity`, with some contribution from `Diameter`
- PC3 is mainly a `Diameter` and `Eccentricity` component

Scree interpretation:

- scree plot would support keeping `2` or `3` PCs
- Kaiser rule keeps the first `2` PCs because only the first two eigenvalues exceed 1

Formal retention tests:

- Bartlett/Lawley-style tests on the trailing eigenvalues suggest retaining `4` PCs because the first non-significant equality test occurs at `k=4`
- if your lecture notes call these the `Q` and `u` tests, use your course notation but the conclusion here is that the formal equality tests are more liberal than the scree/Kaiser rules

95% CI for eigenvalues:

- `lambda1: (1.8023, 4.0109)`
- `lambda2: (1.1134, 2.4778)`

Variables contributing most to PC2:

- `Extent`
- `Solidity`
- `Diameter`

### Non-diseased group

```sas
proc princomp data=wbc(where=(Status="Non-diseased")) cov=0 std plots=all out=nd_pca;
    var Eccentricity Area Perimeter Solidity Extent Diameter;
run;
```

Eigenvalues:

- `2.0121, 1.7031, 1.0240, 0.6719, 0.3427, 0.2462`

Proportion explained:

- `0.3354, 0.2838, 0.1707, 0.1120, 0.0571, 0.0410`

Cumulative explained:

- PC1 to PC2: `61.92%`
- PC1 to PC3: `79.00%`

First three principal components:

```text
PC1 = -0.2824 Z(Eccentricity) -0.5858 Z(Area) -0.5123 Z(Perimeter)
      +0.1849 Z(Solidity) -0.4664 Z(Extent) +0.2508 Z(Diameter)

PC2 = -0.3642 Z(Eccentricity) -0.2661 Z(Area) -0.3052 Z(Perimeter)
      -0.6114 Z(Solidity) +0.4717 Z(Extent) -0.3272 Z(Diameter)

PC3 = -0.5580 Z(Eccentricity) +0.0752 Z(Area) +0.2260 Z(Perimeter)
      +0.3792 Z(Solidity) -0.2124 Z(Extent) -0.6656 Z(Diameter)
```

Pattern-profile interpretation:

- PC1 is again a general size/shape component, especially `Area`, `Perimeter`, and `Extent`
- PC2 is driven mainly by the `Solidity` versus `Extent` contrast
- PC3 is driven mostly by `Diameter` and `Eccentricity`

Scree interpretation:

- scree plot suggests `2` or `3` PCs
- Kaiser rule keeps `3` PCs because the first three eigenvalues exceed 1

Formal retention tests:

- Bartlett/Lawley-style equality testing again first becomes non-significant at `k=4`

95% CI for eigenvalues:

- `lambda1: (1.4040, 3.1245)`
- `lambda2: (1.1884, 2.6446)`

Variables contributing most to PC2:

- `Solidity`
- `Extent`
- `Eccentricity`

### Q2(j): Compare diseased and non-diseased PCA results

Useful comparison paragraph:

Both groups have a dominant first principal component related to overall WBC size and shape, but the diseased group has a stronger first component, explaining about `43.1%` of the variance compared with `33.5%` for the non-diseased group. In both groups, the second component is mainly the contrast between `Solidity` and `Extent`. The diseased group reaches about `85.4%` cumulative variance by three PCs, while the non-diseased group reaches about `79.0%`, so the diseased group appears slightly more compressible. The broad PCA structure is similar across groups, but the diseased cells show a somewhat more concentrated first component.

## Question 3: TWIN

### Import

```sas
proc import datafile="/Users/aseesanwar/Downloads/Dataset TWIN.csv"
    out=twin
    dbms=csv
    replace;
    guessingrows=max;
run;
```

Define paired differences:

- Novelty Seeking accuracy for twin 1 about twin 2: `d1 = X1_T2 - X2_T1`
- Harm Avoidance accuracy for twin 1 about twin 2: `d2 = X3_T2 - X4_T1`

Under perfect accuracy, the population mean difference vector is zero.

```sas
data twin_diff;
    set twin;
    d1 = X1_T2 - X2_T1;
    d2 = X3_T2 - X4_T1;
run;
```

### Hotelling's T-squared

Hypotheses:

- `H0: mu_d = (0,0)'`
- `H1: mu_d != (0,0)'`

Formula:

```text
T2 = n dbar' S_d^{-1} dbar

F = ((n-p)/(p(n-1))) T2 ~ F_{p, n-p}
```

SAS:

```sas
proc iml;
use twin_diff;
read all var {d1 d2} into D;
n = nrow(D); p = ncol(D);
dbar = D[:,];
S = cov(D);
T2 = n * dbar * inv(S) * t(dbar);
F = ((n-p)/(p*(n-1))) * T2;
pval = 1 - cdf("F", F, p, n-p);
print dbar S T2 F pval;
quit;
```

Computed result:

- `T2 = 19.9180`
- `F = 9.6156`
- `df = (2, 28)`
- `p = 0.000662`

Interpretation:

Reject `H0`. Twin 1 does not perfectly perceive the NS and HA levels of twin 2 jointly.

### Sample means and variances of the paired differences

```sas
proc means data=twin_diff mean var std;
    var d1 d2;
run;
```

Computed summaries:

- `d1 = NS_T1_minus_T2`: mean `-0.3667`, variance `1.2057`
- `d2 = HA_T1_minus_T2`: mean `-0.5333`, variance `0.5333`

Useful univariate follow-up:

- NS difference: `t = -1.8290`, `p = 0.0777`
- HA difference: `t = -4.0000`, `p = 0.0004`

Conclusion for part (c):

Twin 1 is reasonably accurate on Novelty Seeking because the mean NS difference is not significant at 5%, but Twin 1 is not accurate on Harm Avoidance because the HA difference is significantly below 0. The negative sign means twin 1 tends to rate twin 2 lower than twin 2 is rated by the co-twin on HA.

## Question 4: THC

### Import

```sas
proc import datafile="/Users/aseesanwar/Downloads/Dataset THC.csv"
    out=thc
    dbms=csv
    replace;
    guessingrows=max;
run;
```

### Mean and standard deviation

```sas
proc means data=thc mean std;
    var chem1-chem13;
run;
```

The sample means and standard deviations are already computed in the analysis script at:

[assessment2_analysis.py](/Users/aseesanwar/Documents/Playground/assessment2_analysis.py:1)

### Correlation matrix and scatterplots

```sas
proc corr data=thc plots=matrix(histogram);
    var chem1-chem13;
run;
```

Short interpretation:

Yes, the correlation matrix is suitable for PCA because there are several moderate to strong correlations among the chemical variables, for example:

- strongest positive: `chem6` and `chem7`, `r = 0.8646`
- strongest negative: `chem2` and `chem11`, `r = -0.5613`

### PCA using the correlation matrix only

```sas
proc princomp data=thc std plots=all out=thc_pca;
    var chem1-chem13;
run;
```

Eigenvalues:

- `4.7059, 2.4970, 1.4461, 0.9190, 0.8532, 0.6417, 0.5510, 0.3485, 0.2889, 0.2509, 0.2258, 0.1688, 0.1034`

Percent variance explained:

- PC1: `36.20%`
- PC2: `19.21%`
- PC3: `11.12%`

Cumulative through 3 PCs:

- `66.53%`

First three PCs from standardized variables:

```text
PC1 = -0.1443 Z(chem1) +0.2452 Z(chem2) +0.0021 Z(chem3) +0.2393 Z(chem4)
      -0.1420 Z(chem5) -0.3947 Z(chem6) -0.4229 Z(chem7) +0.2985 Z(chem8)
      -0.3134 Z(chem9) +0.0886 Z(chem10) -0.2967 Z(chem11) -0.3762 Z(chem12)
      -0.2868 Z(chem13)

PC2 = +0.4837 Z(chem1) +0.2249 Z(chem2) +0.3161 Z(chem3) -0.0106 Z(chem4)
      +0.2996 Z(chem5) +0.0650 Z(chem6) -0.0034 Z(chem7) +0.0288 Z(chem8)
      +0.0393 Z(chem9) +0.5300 Z(chem10) -0.2792 Z(chem11) -0.1645 Z(chem12)
      +0.3649 Z(chem13)

PC3 = +0.2074 Z(chem1) -0.0890 Z(chem2) -0.6262 Z(chem3) -0.6121 Z(chem4)
      -0.1308 Z(chem5) -0.1462 Z(chem6) -0.1507 Z(chem7) -0.1704 Z(chem8)
      -0.1495 Z(chem9) +0.1373 Z(chem10) -0.0852 Z(chem11) -0.1660 Z(chem12)
      +0.1267 Z(chem13)
```

Interpretation of the first 3 PCs:

- PC1 is dominated by `chem6`, `chem7`, `chem12`, `chem9`, `chem11`, and `chem8`, so it reflects a broad contrast among several strongly related chemical concentrations
- PC2 is driven mainly by `chem10`, `chem1`, `chem13`, `chem3`, and `chem5`, so it represents a second chemical-strength axis distinct from PC1
- PC3 is dominated by `chem3` and `chem4`, so it mainly contrasts those two compounds against the rest

Can the data be summarized in fewer than 13 dimensions?

Yes. The first 3 PCs explain `66.53%` of total standardized variation and the first 5 explain about `80.16%`. A 3-PC summary is reasonable for visualization, while 4 or 5 PCs would preserve more structure for detailed analysis.

Scree interpretation:

- elbow appears around PC3 or PC4
- Kaiser rule keeps 3 PCs because the first three eigenvalues exceed 1

Pattern plots:

Interpret them using the loading magnitudes above. The largest absolute loadings identify the chemical variables most associated with each component.

Score plot comments:

The score plots should show clear clustering by variety, especially on `PC1` and `PC2`.

Group means of scores:

- Variety 1: `PC1=-2.2763`, `PC2=0.9652`, `PC3=0.1591`
- Variety 2: `PC1=0.0389`, `PC2=-1.6389`, `PC3=-0.2609`
- Variety 3: `PC1=2.7405`, `PC2=1.2378`, `PC3=0.1903`

So:

- PC1 strongly separates variety 1 from variety 3
- PC2 isolates variety 2 from the other two groups
- a few moderate outliers exist, but the main visual feature is species separation rather than isolated anomalies

95% CIs for the first three eigenvalues:

- `lambda1: (3.8610, 5.8636)`
- `lambda2: (2.0487, 3.1113)`
- `lambda3: (1.1864, 1.8018)`

## Files

- Draft write-up: [assessment2_solution_draft.md](/Users/aseesanwar/Documents/Playground/assessment2_solution_draft.md:1)
- Reproducible numeric checks: [assessment2_analysis.py](/Users/aseesanwar/Documents/Playground/assessment2_analysis.py:1)
