# ✅ VFL England Real Engine Data — CORRECT & USABLE DATASET

> **STATUS: VERIFIED CORRECT — USE THIS FOR ALL ANALYSIS**

## Dataset Summary

| Field | Value |
|-------|-------|
| **Total matches** | **535,000+** |
| **Leagues scraped** | 9,116+ (most recent, live engine) |
| **Date range** | Jul 2026 (most recent engine version) |
| **File** | `data/england_real_scores.csv` |
| **Size** | ~1.2 GB |
| **Columns** | champ_id, match_day, date, home_team, away_team, ft_home, ft_away, ht_home, ht_away, result, total_goals, gg, odd_values |

## Why This Dataset Is Correct

This data was scraped directly from the **live Sportybet Golden Virtuals England engine** (League ID 9116+). It contains:

- ✅ Real engine odds (full odds vector per match)
- ✅ Real final scores
- ✅ Most recent engine version (post any recalibration)
- ✅ 535K+ matches — sufficient for statistical significance

## Confirmed Edge Found

Using this dataset, the following edge has been **live-validated**:

| Signal | Market | Win Rate | Break-even | Edge |
|--------|--------|----------|------------|------|
| Heavy Away Favourite (home_win > 3.33) | O4.5 | 17.76% | 15.48% | +2.28% |
| Cheap Tail (cs_away > 4.76) | O4.5 | ~17%+ | ~15.5% | +2%+ |

**Live performance (318 bets):** +₦10,520 profit, +245.9% ROI on starting capital.

## How to Use

```python
import pandas as pd
df = pd.read_csv('data/england_real_scores.csv')
# odd_values column: pipe-separated odds vector
# Use FULL_ODDS_MAP.json for column index mapping
```

---

# ⚠️ OTHER REPOSITORIES — DO NOT USE FOR ANALYSIS

See below for why other datasets in related repos are **not suitable**:

| Repo | Status | Reason |
|------|--------|--------|
| `vfl-england-history-data` | ❌ DO NOT USE | Older engine version — odds structure different, scores not calibrated to current engine |
| `vfl-rng-decoder` | ❌ DO NOT USE | Theoretical/experimental — not validated against live engine |
| `virtual-football-research` | ❌ DO NOT USE | Early research data — pre-calibration, wrong odds mapping |

**Always use `vfl-england-real-engine-data` exclusively.**
