from __future__ import annotations

from pathlib import Path

import pandas as pd


def main() -> None:
    xlsx_path = Path(__file__).resolve().parents[1] / "Assests_Trust_Level_Stride.xlsx"
    if not xlsx_path.exists():
        raise SystemExit(f"XLSX not found: {xlsx_path}")

    print(f"path: {xlsx_path}")
    xl = pd.ExcelFile(xlsx_path)
    print("sheets:", xl.sheet_names)

    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        df.columns = [str(c).strip() for c in df.columns]
        print("\n===", sheet, "===")
        print("shape:", df.shape)
        print("columns:", list(df.columns))
        with pd.option_context("display.max_columns", 30, "display.width", 220):
            print(df.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
