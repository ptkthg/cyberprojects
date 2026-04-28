from __future__ import annotations

from io import BytesIO

import pandas as pd


def to_csv_bytes(rows: list[dict]) -> bytes:
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


def dataframe_from_rows(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)
