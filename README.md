# VFL Real Engine Data — England (CORRECTED 2026-08-03)

---

## ✅ DATASET 1: VFL England — `data/england_part1.csv` + `data/england_part2.csv`

| Field | Value |
|-------|-------|
| **Rows** | **989,970** (990,000 scraped minus 30 matches from 3 cancelled matchdays: eBlocks 253523, 253529, 253531) |
| **Coverage** | January 1, 2026 → July 25, 2026 (eBlockIds 252363 → 351362, zero gaps) |
| **Status** | ✅ **VERIFIED CORRECT — server-validated 2026-08-03** (this time with proof, see below) |
| **Storage** | Git LFS (~1.1 GB each) |

### England Columns
`eblock_id, match_order, date_utc, home, away, ht_home, ht_away, ft_home, ft_away, result, total_goals, gg, odd_values`

- `match_order` = position 1–10 within the matchday (**repaired 2026-08-03**; was broken/all-1s in the original)
- `ft_home` / `ft_away` = full-time goals ✅ **REAL — fetched from the game server** (`/eventBlocks/event/result`) for every matchday
- `ht_home` / `ht_away` = half-time goals ✅ verified 100.000% (989,970/989,970) against server
- `result`, `total_goals`, `gg` = recomputed from the REAL ft columns
- `odd_values` = 450-value pipe-separated float array per match ✅ real (overrounds match live engine)

### What was wrong before (2026-08-03 correction)
The previous version of these files had **contaminated `ft_home`/`ft_away`/`result`/`total_goals`/`gg` columns** —
they contained half-time goal values from misaligned rows, not full-time results. Signatures of the corruption:
`total_goals` maxed at 3 across all rows, `ft < ht` in ~46% of rows (physically impossible), and ~chance-level
agreement with server results. **Every analysis or "edge" derived from those columns was invalid** (95% Under-2.5
"locks", decimal-trap patterns, the "O4.5 edge" — all artifacts of the fake columns, now permanently retired).

The fix: all 99,000 matchdays were re-fetched from the server (results-only endpoint) and positionally joined to
the scraped rows. Join integrity: **989,970/989,970 = 100.000%** half-time agreement (worst 10,000-match window: 100.00%).
Physics: `ft >= ht` holds for 100% of rows. Base rates now: Home 43.4% / Draw 24.7% / Away 31.9%, avg ~2.81 goals.

### Engine facts discovered (use these, not intuition)
- **The engine caps match totals at 6 goals** (6-goal games = 5.3% of matches; zero 7+ goal games in 989,970 matches — confirmed in two independent data sources).
- Total-goals distribution: 0: 5.9%, 1: 15.8%, 2: 23.8%, 3: 22.4%, 4: 16.9%, 5: 9.9%, 6: 5.3%
- Bookmaker margins: 1X2 = 5.26% | O/U = 5.3% | GG/NG = 8.4% | HT markets ≈ 10.1%
- **Pricing is TABLE_ODDS**: odds derive from current league standings + team priors.

### Key odd_values indices (confirmed against live playlist 41104 market map)
| Index | Market |
|-------|--------|
| `[0]` | Home Win 1X2 |
| `[1]` | Away Win 1X2 (**swapped from intuitive order**) |
| `[2]` | Draw 1X2 |
| `[12..14]` | Double Chance: DrawAway, HomeAway, HomeDraw |
| `[50]` / `[51]` | NG / GG |
| `[52..61]` | O/U 0.5–4.5 — **UNDER comes first in each pair**: 52=U0.5, 53=O0.5, 54=U1.5, 55=O1.5, 56=U2.5, 57=O2.5, 58=U3.5, 59=O3.5, 60=U4.5, 61=O4.5 |
| `[124..126]` | HT 1X2 (Home, Draw, Away) |
| `[356..359]` | HT O/U 0.5/1.5 (Under-first pairs) |

⚠️ Getting the O/U pair order wrong fabricates phantom "edges" with z-scores of +40 or more. Always check against the market map.

### Calibration verdict (989,970 matches, 70/30 chronological out-of-sample split)
A full pricing-edge scan was run on this corrected dataset: odds bands (1X2, O/U, GG), table-conditional
(rank difference × odds ≥ 2.0), form-conditional, GD-conditional, season-phase (round 1 → 20+), team-level
(all 20 clubs, home & away), fine 2D grids (Bonferroni-corrected), and time drift (10 deciles, Jan→Jul).
**Every cell is calibrated: hit rate ≈ margin-normalized implied probability, ROI ≈ −5% (the margin), no
out-of-sample z > 3 pocket exists.** The engine prices standings information exactly. Any betting system on
this league bleeds the margin. Dataset value is research/fairness-audit, not advantage play.

---

## ❌ DATASET 2 (DELETED): VFL Africa Cup of Nations — `data/afcon_history.csv`

**Deleted 2026-08-03.** Audit found the same contamination as the old England files: `ft < ht` in 48.3% of rows
(physically impossible) and `total_goals` capped at 3 — the ft/result/total_goals/gg columns were HT-goal values
from misaligned rows, not full-time results. It cannot be repaired without a server-side AFCON results backfill
(playlist 14122), which has not been run. Do not use any copy of this file for ft-based analysis.

---

## DELETED EARLIER (still do not use)

| File | Reason |
|------|--------|
| `england_seasons_7838_to_new.csv` | CORRUPTED — ft columns contained HT goals (same bug family). Invalid. |
| `data/chunk_aa.gz` … `chunk_af.gz` | Old chunked format, superseded. |

## Usage

```python
import pandas as pd
df = pd.concat([pd.read_csv("data/england_part1.csv"),
                pd.read_csv("data/england_part2.csv")], ignore_index=True)
# rows are in DESCENDING time order (most recent first); match_order 1-10 within each eblock_id
```

```bash
git lfs install
git clone https://github.com/Tomriddle004/vfl-england-real-engine-data.git
```

## Scrapers
`scrapers/scrape_real_v5.py` — historical; the script that produced the published columns is not in this repo.
The 2026-08-03 correction did NOT re-scrape odds/fixtures (verified real); it re-fetched results from the server
and rebuilt the result columns from first principles.
