# VFL England Real Engine Data

## ✅ AUTHORITATIVE DATASET — `data/england_real_scores.csv`

| Field | Value |
|-------|-------|
| **Rows** | **535,000** (535,001 including header) |
| **File** | `data/england_real_scores.csv` |
| **Storage** | Git LFS (1.2 GB) |
| **LFS SHA** | `35de5d905d8264c79549389eb72e5d50165dd53b2069b48ca3c58f1998accd14` |
| **Status** | ✅ VERIFIED CORRECT — use for ALL analysis |

### Columns
`champ_id, match_day, date, home_team, away_team, ft_home, ft_away, ht_home, ht_away, result, total_goals, gg, odd_values`

### Validation
- `ft_home` / `ft_away` = full-time goals (confirmed correct)
- `ht_home` / `ht_away` = half-time goals (confirmed correct)
- `odd_values` = 450-element JSON array of live odds at match start

---

## ❌ DELETED DATASETS — DO NOT USE

The following datasets have been **permanently removed** from this repository:

| File | Rows | Reason |
|------|------|--------|
| `england_seasons_7838_to_new.csv` | 423,061 | **CORRUPTED** — `ft_home`/`ft_away` columns contain HT goals, not FT goals. All analysis on this file is invalid. |
| `data/chunk_aa.gz` … `chunk_af.gz` | — | Old chunked format, superseded by LFS CSV. |

**If you encounter `england_seasons_7838_to_new.csv` anywhere on the cloud computer, do not use it for any analysis. It is corrupted.**

---

## Usage

```python
import pandas as pd
df = pd.read_csv("data/england_real_scores.csv")
# df has 535,000 rows — ft_home/ft_away are FULL TIME goals
```

To clone with LFS data:
```bash
git lfs install
git clone https://github.com/Tomriddle004/vfl-england-real-engine-data.git
```
