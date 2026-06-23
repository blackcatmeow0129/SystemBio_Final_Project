# Kang & Kim 2024 — CRE Enhancer Thermodynamic Model Reproduction

> **Paper**: Deep molecular learning of transcriptional control of a synthetic CRE enhancer and its variants  
> **Authors**: Chan-Koo Kang, Ah-Ram Kim  
> **Journal**: iScience 27, 108747 (January 2024)  
> **DOI**: [https://doi.org/10.1016/j.isci.2023.108747](https://doi.org/10.1016/j.isci.2023.108747)

This repository contains code and protocols to reproduce Figures 2C, 3A, 3B/C, 3D/E, 4D/K, and 5A/E/G from the above paper using publicly available supplementary data and the [transcpp](https://github.com/kennethabarr/transcpp) thermodynamic model.

---

## Reproduced Figures

| Figure | Description | Status | Platform |
|---|---|---|---|
| Figure 2C | 4TF self-competition model, single-hit fitting | ✅ Done | Mac / Server |
| Figure 3A | R-value by TF type (non-family vs CREB family) | ✅ Done | Server |
| Figure 3B | Without self-competition, fitting R by # of TFs | ✅ Done | Windows + Server |
| Figure 3C | Without self-competition, multi-hit prediction R | ✅ Done | Windows + Server |
| Figure 3D | With self-competition, fitting R by # of TFs | ✅ Done | Mac + Server |
| Figure 3E | With self-competition, multi-hit prediction R | ✅ Done | Server |
| Figure 4D | Scatter plot, thermodynamic model vs experiment | ✅ Done | Mac / Server |
| Figure 4K | QSAM multi-hit prediction | ✅ Done | Mac / Server |
| Figure 5A/G | Δactivity bar plot (→A and →T substitutions) | ✅ Done | Mac / Server |
| Figure 5E | TF activation coefficients | ✅ Done | Mac / Server |

---

## Repository Structure

```
kang2024-cre-reproduction/
│
├── README.md
├── .gitignore
├── requirements.txt
│
├── data/
│   └── README.md                        # How to download mmc2/3/4
│
├── environment/
│   ├── install_transcpp_mac.sh          # Build transcpp on Mac M1
│   ├── install_transcpp_linux.sh        # Build transcpp on Linux
│   └── transcpp_printRate_patch.cpp     # Required patch for rates output
│
├── figures/
│   ├── Figure2C/
│   │   ├── generate_figure2c.py
│   │   └── output/Figure2C.png
│   ├── Figure3A/
│   │   ├── generate_figure3a_xmls.py
│   │   ├── run_figure3a.sh
│   │   ├── plot_figure3a.py
│   │   └── output/Figure3A.png
│   ├── Figure3BC/
│   │   ├── build_figure3bc.py
│   │   ├── selected_fit_manifest.tsv
│   │   └── output/
│   │       ├── Figure3B.png
│   │       ├── Figure3C.png
│   │       └── Figure3_BC.png
│   ├── Figure3DE/
│   │   ├── generate_figure3de_xmls.py
│   │   ├── run_figure3de_local.sh       # Mac M1: n1~n4
│   │   ├── run_figure3de_server.sh      # Server: n5~n7 (reverse order)
│   │   ├── generate_figure3e_mh.py      # multi-hit XML for Fig3E
│   │   ├── run_figure3e_mh.sh
│   │   ├── plot_figure3de.py
│   │   └── output/
│   │       ├── Figure3D.png
│   │       ├── Figure3E.png
│   │       └── Figure3DE.png
│   ├── Figure4DK/
│   │   ├── generate_figure4d.py
│   │   ├── generate_figure4k_qsam.py
│   │   └── output/
│   │       ├── Figure4D.png
│   │       └── Figure4K.png
│   └── Figure5/
│       ├── generate_figure5ag.py
│       ├── generate_figure5e.py
│       └── output/
│           ├── Figure5AG.png
│           └── Figure5E.png
│
└── protocols/
    ├── FIGURE2_PROTOCOL_KO.md
    ├── FIGURE3_PROTOCOL_KO.md
    └── TIPS_AND_TROUBLESHOOTING.md
```

---

## Quick Start

### Step 1 — Download supplementary data

Go to [https://doi.org/10.1016/j.isci.2023.108747](https://doi.org/10.1016/j.isci.2023.108747) and download:

| File | Content |
|---|---|
| `mmc2.xlsx` | Model parameters (4TF_self, 7TF, 7TF_self) |
| `mmc3.xlsx` | TF position weight matrices (PWMs) |
| `mmc4.xlsx` | Sequences and MPRA expression levels |

Save to `data/`:
```
data/
├── 1-s2.0-S2589004223028249-mmc2.xlsx
├── 1-s2.0-S2589004223028249-mmc3.xlsx
└── 1-s2.0-S2589004223028249-mmc4.xlsx
```

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Build transcpp

**Mac M1:**
```bash
bash environment/install_transcpp_mac.sh
```

**Linux (Ubuntu):**
```bash
bash environment/install_transcpp_linux.sh
```

### Step 4 — Apply printRate patch (required)

By default, transcpp does not save a rates file. Apply the patch in `environment/transcpp_printRate_patch.cpp` to `transcpp/src/main/transcpp.cpp`, then recompile.

The patch adds these lines immediately after `fly_sa->writeResult();`:
```cpp
ofstream ratefile((xmlname+".rates").c_str());
embryo.printRate(ratefile, false);
ratefile.close();
```

### Step 5 — Create working directories

```bash
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/sequences
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3a_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3b_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_mh_xmls
```

> ⚠️ **transcpp must always be run from the `fits/` directory**, because FASTA paths are relative.

---

## Figure-by-Figure Guide

### Figure 2C

**Platform**: Mac or Server  
**Time**: ~1 minute  
**Description**: Predicts single-hit MPRA expression using the 4TF self-competition model (CREB1, CREM, ATF1, ATF7) and compares with experiment.

**Data used**:
- `mmc2.xlsx` sheet `4TF_self` → Model 5 parameters (anneal=false)
- `mmc3.xlsx` → PWMs for CREB1, CREM, ATF1, ATF7
- `mmc4.xlsx` sheet `single-hit` → 261 sequences + expression levels

**Differences from paper**:

| Item | Paper | This repo |
|---|---|---|
| TF set | 7TF (`7TF_self`) | 4TF (`4TF_self` Model 5) |
| Optimization | Re-fit with annealing | mmc2 params as-is (anneal=false) |
| Pearson R | ~0.88 | 0.801 |

**Run**:
```bash
python3 figures/Figure2C/generate_figure2c.py \
    --data-dir data/ \
    --transcpp ~/cre_reproduction/transcpp/transcpp \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits
```

---

### Figure 3A

**Platform**: Server (Linux, recommended)  
**Time**: ~2 days (10 parallel jobs)  
**Description**: Adds each of 21 TFs (14 non-family + 7 CREB family) alongside CREB1 and measures fitting R.

**Data used**:
- `mmc2.xlsx` sheet `7TF_self` → initial parameters
- `mmc3.xlsx` → family TF PWMs
- JASPAR API → non-family TF PWMs (auto-cached to `non_family_pwms.pkl`)
- `mmc4.xlsx` sheet `single-hit` → 261 training sequences

**Run**:
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits

# 1. Generate XMLs (168 = 21 TFs × 8 models)
python3 figures/Figure3A/generate_figure3a_xmls.py --data-dir /path/to/data

# 2. Run transcpp (10 parallel)
nohup bash figures/Figure3A/run_figure3a.sh > ~/fig3a_log.txt 2>&1 &

# 3. Plot (when 168/168 rates files are done)
python3 figures/Figure3A/plot_figure3a.py
```

---

### Figure 3B/C

**Platform**: Windows (team member) + Server  
**Time**: ~3 days (two computers in parallel)  
**Description**:
- **3B**: SelfCompetition=false, 127 TF combinations, single-hit fitting R
- **3C**: Same models applied to multi-hit 722 sequences (no additional training)

**Key insight**: 3C reuses 3B's fitted parameters with `anneal=false` applied to multi-hit sequences. No separate training is needed.

**Data used**:
- `mmc4.xlsx` sheet `single-hit` → 261 training sequences (3B)
- `mmc4.xlsx` sheet `multi-hit` → 722 prediction sequences (3C)

**Differences from paper**:

| Item | Paper | This repo |
|---|---|---|
| Runs per combination | 8 | 4 (time constraint) |
| SelfCompetition | false | false |

**Run**:
```bash
python3 figures/Figure3BC/build_figure3bc.py \
    --transcpp /path/to/transcpp \
    --data-dir data/ \
    --runs 4 \
    --parallel 4
```

---

### Figure 3D/E

**Platform**: Mac M1 (n1–n4) + Linux Server (n5–n7)  
**Time**: ~4 days local + ~several hours on server  
**Description**:
- **3D**: SelfCompetition=true, 127 TF combinations, single-hit fitting R
- **3E**: Same models, multi-hit prediction R

> ⚠️ **Mac M1 segfaults when predicting 722 multi-hit sequences.**  
> Fig3E must be run on a Linux server.

**Platform split strategy**:

| Platform | Handles | Reason |
|---|---|---|
| Mac M1 (7 parallel) | n=1~4 (fewer TFs) | Better single-core performance |
| Server (25 parallel) | n=5~7 (more TFs, reverse order) | More cores |

**Run on Mac (n1–n4)**:
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 figures/Figure3DE/generate_figure3de_xmls.py --data-dir /path/to/data
nohup bash figures/Figure3DE/run_figure3de_local.sh > ~/fig3de_local_log.txt 2>&1 &
```

**Run on Server (n5–n7, reverse)**:
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 figures/Figure3DE/generate_figure3de_xmls.py --data-dir /path/to/data
nohup bash figures/Figure3DE/run_figure3de_server.sh > ~/fig3de_server_log.txt 2>&1 &
```

**Transfer local rates to server, then run Fig3E**:
```bash
# Transfer rates files to server
scp -J <jump_server> \
    ~/cre_reproduction/.../fig3de_xmls/*.rates \
    user@server:~/cre_reproduction/.../fig3de_xmls/

# Generate multi-hit XMLs and run on server
python3 figures/Figure3DE/generate_figure3e_mh.py
nohup bash figures/Figure3DE/run_figure3e_mh.sh > ~/fig3e_log.txt 2>&1 &

# Plot
python3 figures/Figure3DE/plot_figure3de.py
```

**Key XML settings**:
```xml
<annealer_input init_T="100000" lambda="0.0001" init_loop="100000"/>
<Mode>
    <NumThreads value="1"/>          <!-- Always 1 on server -->
    <SelfCompetition value="true"/>
    <Seed value="{run_number}"/>
</Mode>
```

---

### Figure 4D/K

**Platform**: Mac or Server  
**Time**: ~1 minute (4K), ~several minutes (4D)

**Figure 4D** — scatter plot of 4TF model predictions vs experiment  
**Figure 4K** — QSAM (linear model) multi-hit prediction (R=0.856)

**Differences from paper**:

| Item | Paper | This repo |
|---|---|---|
| 4D model | Re-optimized 4TF | mmc2 Model 5 params (anneal=false) |
| 4K model | Linear QSAM | Ridge regression (equivalent) |
| 4K R | ~0.87 | 0.856 |

**Run**:
```bash
# Figure 4D
python3 figures/Figure4DK/generate_figure4d.py --data-dir data/

# Figure 4K (no transcpp needed)
python3 figures/Figure4DK/generate_figure4k_qsam.py --data-dir data/
```

---

### Figure 5A/E/G

**Platform**: Mac or Server  
**Time**: ~1 minute

**Figure 5A/G** — Δactivity bar plots for →A and →T substitutions  
**Figure 5E** — TF activation coefficients (log10 scale)

**Run**:
```bash
python3 figures/Figure5/generate_figure5ag.py --data-dir data/
python3 figures/Figure5/generate_figure5e.py --data-dir data/
```

---

## Platform Summary

| Figure | Mac M1 | Windows | Linux Server |
|---|---|---|---|
| 2C | ✅ | ✅ | ✅ |
| 3A | ⚠️ slow | ⚠️ slow | ✅ recommended |
| 3B/C | ✅ | ✅ team member | ✅ recommended |
| 3D (n1–4) | ✅ recommended | ✅ | ✅ |
| 3D (n5–7) | ⚠️ very slow | ⚠️ | ✅ recommended |
| 3E | ❌ segfault | ✅ | ✅ required |
| 4D/K | ✅ | ✅ | ✅ |
| 5A/E/G | ✅ | ✅ | ✅ |

---

## Estimated Runtime

| Figure | Platform | Time |
|---|---|---|
| 2C | Mac M1 | ~1 min |
| 3A | Server (10 parallel) | ~2 days |
| 3B/C | 2 computers | ~3 days |
| 3D n1–4 | Mac M1 (7 parallel) | ~4 days |
| 3D n5–7 | Server (25 parallel) | ~several hours |
| 3E | Server (25 parallel) | ~several hours |
| 4K | Mac M1 | ~1 min |
| 5A/E/G | Mac M1 | ~1 min |

---

## Key Notes

1. **Run transcpp from the `fits/` directory** — FASTA paths are relative
2. **Mac M1 segfaults on 722 multi-hit sequences** — use Linux server for Fig3E
3. **Use `NumThreads=1` with high process parallelism** on server (e.g. 25 jobs × 1 thread = 25 cores)
4. **Kill the nohup script before killing transcpp** — otherwise new processes keep spawning
5. **FASTA files must use 60-character line wrapping**
6. **`init_loop=100` for quick trend check**, `init_loop=100000` for paper-quality results
7. **Fig3C and 3E reuse 3B and 3D parameters** — no extra training needed

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Could not open file sequences/...` | Wrong working directory | Run from `fits/` directory |
| Segmentation fault (multi-hit) | Mac M1 memory limit | Run on Linux server |
| Floating point exception | Duplicate gene names in XML | Add prefix to gene names |
| All predicted values identical | Duplicate `<Source>` tags in XML | Rebuild XML from scratch |
| Processes keep respawning | nohup script still alive | `pkill -9 -f run_fig3` before `pkill -9 -f transcpp` |

---

## Citation

```bibtex
@article{kang2024deep,
  title={Deep molecular learning of transcriptional control of a synthetic CRE enhancer and its variants},
  author={Kang, Chan-Koo and Kim, Ah-Ram},
  journal={iScience},
  volume={27},
  number={1},
  pages={108747},
  year={2024},
  publisher={Elsevier},
  doi={10.1016/j.isci.2023.108747}
}
```

---

## Acknowledgements

- [transcpp](https://github.com/kennethabarr/transcpp) and [neoParSA](https://github.com/kennethabarr/neoParSA) by Kenneth Barr and John Reinitz
- Original MPRA data from [Melnikov et al. 2012](https://doi.org/10.1038/nbt.2137)
