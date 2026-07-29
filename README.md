# VFL Real Engine Data — England + Africa Cup of Nations

---

## ✅ DATASET 1: VFL England — `data/england_part1.csv` + `data/england_part2.csv`

| Field | Value |
|-------|-------|
| **Rows** | **990,000** |
| **Files** | `data/england_part1.csv` + `data/england_part2.csv` (split due to 2 GB LFS limit) |
| **Storage** | Git LFS (~1.1 GB each) |
| **Coverage** | January 1, 2026 → July 25, 2026 |
| **Scraped** | 2026-07-25 via `scrape_full_history.py` |
| **Status** | ✅ VERIFIED CORRECT |

### England Columns
`eblock_id, match_order, date_utc, home, away, ht_home, ht_away, ft_home, ft_away, result, total_goals, gg, odd_values`

- `ft_home` / `ft_away` = full-time goals ✅ 100% populated
- `ht_home` / `ht_away` = half-time goals ✅ 100% populated
- `odd_values` = 450-value pipe-separated float array per match
- Teams: 10 per round (standard Premier League clubs)

### Key odd_values Indices (England, confirmed)
| Index | Market |
|-------|--------|
| `[0]` | Home Win 1X2 |
| `[1]` | Away Win 1X2 (**NOTE: swapped from intuitive order**) |
| `[2]` | Draw 1X2 |
| `[50]` | No Goals (NG) |
| `[51]` | Both Teams Score (GG) |
| `[359]` | HT Over 1.5 (binary) |

---

## ✅ DATASET 2: VFL Africa Cup of Nations — `data/afcon_history.csv`

| Field | Value |
|-------|-------|
| **Rows** | **512,550** |
| **File** | `data/afcon_history.csv` |
| **Storage** | Git LFS (25 MB) |
| **Coverage** | January 1, 2026 → July 29, 2026 |
| **Scraped** | 2026-07-29 via `scrape_afcon_history.py` |
| **Status** | ✅ VERIFIED CORRECT |
| **CONTENT_ID** | 14122 (`league_africacup2024`) |
| **Live CALC_ID** | 517930 |
| **History CALC_ID** | None (omit from `/eventBlocks/find` query) |

### AFCON Columns
`eblock_id, match_order, date_utc, home, away, ht_home, ht_away, ft_home, ft_away, result, total_goals, gg, odd_values`

- `ft_home` / `ft_away` = full-time goals ✅ 100% populated
- `ht_home` / `ht_away` = half-time goals ✅ 100% populated
- `odd_values` = pipe-separated float array per match
- Teams (12 per round): CIV, EQG, NGA, GNB, EGY, CPV, GHA, MOZ, SEN, GUI, CAM, GAM

---

## ❌ DELETED DATASETS — DO NOT USE

| File | Rows | Reason |
|------|------|--------|
| `england_seasons_7838_to_new.csv` | 423,061 | **CORRUPTED** — `ft_home`/`ft_away` contain HT goals, not FT goals. All analysis on this file is invalid. |
| `data/chunk_aa.gz` … `chunk_af.gz` | — | Old chunked format, superseded by LFS CSV. |

**If you encounter `england_seasons_7838_to_new.csv` anywhere on the cloud computer, do not use it for any analysis. It is corrupted.**

---

## Usage

```python
import pandas as pd

# England dataset (990K rows, split into 2 parts)
df1 = pd.read_csv("data/england_part1.csv")
df2 = pd.read_csv("data/england_part2.csv")
df_england = pd.concat([df1, df2], ignore_index=True)

# AFCON dataset (512K rows, single file)
df_afcon = pd.read_csv("data/afcon_history.csv")
```

To clone with LFS data:
```bash
git lfs install
git clone https://github.com/Tomriddle004/vfl-england-real-engine-data.git
```
