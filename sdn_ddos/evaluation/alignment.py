"""Strict score/cohort identity checks independent of physical Parquet row order."""
import numpy as np
import pandas as pd


def align_scores(path, rows):
    scores = pd.read_parquet(path)
    if len(scores) != len(rows):
        raise ValueError(f'Score/cohort row-count mismatch in {path}: {len(scores)} != {len(rows)}')
    if scores['row_id'].duplicated().any() or rows['row_id'].duplicated().any():
        raise ValueError(f'Duplicate score/cohort row IDs in {path}')
    joined = rows[['row_id']].merge(scores, on='row_id', how='outer', validate='one_to_one', indicator=True, sort=False)
    if not joined['_merge'].eq('both').all():
        raise ValueError(f'Score/cohort ID sets differ in {path}')
    result = rows[['row_id']].merge(scores, on='row_id', how='left', validate='one_to_one', sort=False)['score'].to_numpy()
    if not np.isfinite(result).all():
        raise ValueError(f'Nonfinite scores in {path}')
    return result
