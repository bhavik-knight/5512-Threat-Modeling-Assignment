from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    xlsx_path = repo_root / "Assests_Trust_Level_Stride.xlsx"

    raw = pd.read_excel(xlsx_path, sheet_name="Sheet3", header=None)

    # Find header row
    header_row = None
    for i in range(len(raw)):
        v = raw.iloc[i, 0]
        if isinstance(v, str) and v.strip() == "ID":
            header_row = i
            break

    print("raw shape:", raw.shape)
    print("header_row:", header_row)
    if header_row is None:
        print(raw.head(10).to_string(index=False))
        return

    print("header row values (0..10):")
    print([raw.iloc[header_row, j] for j in range(min(11, raw.shape[1]))])

    df = raw.iloc[header_row + 1 :].copy()
    df.columns = [str(raw.iloc[header_row, j]).strip() for j in range(raw.shape[1])]
    print("parsed columns:", list(df.columns))

    # show first 20 rows and all columns
    with pd.option_context("display.max_columns", 50, "display.width", 240):
        print(df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
