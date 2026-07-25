# VFL England Real Engine Data

## ✅ AUTHORITATIVE DATASET — `data/england_real_scores.csv`

| Field | Value |
|-------|-------|
| **Rows** | **990,000** (990,001 including header) |
| **Files** | `data/england_part1.csv` + `data/england_part2.csv` |
| **Storage** | Git LFS (~1.1 GB each, split due to 2 GB LFS limit) |
| **Coverage** | January 1, 2026 → July 25, 2026 |
| **Scraped** | 2026-07-25 via `scrape_full_history.py` |
| **Status** | ✅ VERIFIED CORRECT — use for ALL analysis |

### Columns
`eblock_id, match_order, date_utc, home, away, ht_home, ht_away, ft_home, ft_away, result, total_goals, gg, odd_values`

**Part 1** (`england_part1.csv`): rows 1–495,000 (Jul 25 → ~Apr 2026)
**Part 2** (`england_part2.csv`): rows 495,001–990,000 (~Apr → Jan 1, 2026)

### Validation
- `ft_home` / `ft_away` = full-time goals ✅ 100% populated
- `ht_home` / `ht_away` = half-time goals ✅ **100% populated** (decoded from `finalOutcome[0..3]`)
- `odd_values` = 450-value pipe-separated float array per match

### Key odd_values Indices (confirmed)
| Index | Market |
|-------|--------|
| `[0]` | Home Win 1X2 |
| `[1]` | Away Win 1X2 (**NOTE: swapped from intuitive order**) |
| `[2]` | Draw 1X2 |
| `[50]` | No Goals (NG) |
| `[51]` | Both Teams Score (GG) |
| `[359]` | HT Over 1.5 (binary) |

### ⚠️ Old 535K Dataset (replaced 2026-07-25)
The previous `england_real_scores.csv` had 535,000 rows but **ht_home/ht_away were 100% empty** — the scraper's HT decoder never matched any pattern. That file has been replaced by this 990K dataset which has full HT data.

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
