from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class Table:
    title: str
    df: pd.DataFrame


def _find_header_row(raw: pd.DataFrame, first_col_header: str = "ID") -> int:
    for idx in range(len(raw)):
        val = raw.iloc[idx, 0]
        if isinstance(val, str) and val.strip() == first_col_header:
            return idx
    raise ValueError(f"Could not find header row starting with {first_col_header!r}")


def _to_markdown_table(df: pd.DataFrame) -> str:
    # Replace NaN with empty string, stringify all cells.
    df = df.fillna("").astype(str)

    headers = list(df.columns)
    rows = df.values.tolist()

    def esc(cell: str) -> str:
        # Minimal escaping for Markdown tables.
        return cell.replace("\n", "<br>").replace("|", "\\|").strip()

    header_line = "| " + " | ".join(esc(h) for h in headers) + " |"
    align_line = "| " + " | ".join(":---" for _ in headers) + " |"
    row_lines = [
        "| " + " | ".join(esc(str(cell)) for cell in row) + " |" for row in rows
    ]
    return "\n".join([header_line, align_line, *row_lines])


def _load_sheet1_assets_and_trust(xlsx_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(xlsx_path, sheet_name="Sheet1", header=None)
    header_row = _find_header_row(raw, "ID")

    # Assets table is in columns 0..5 (inclusive). Column 6 is blank spacer.
    assets_cols = list(range(0, 6))
    trust_cols = list(range(7, 13))

    assets_headers = raw.iloc[header_row, assets_cols].tolist()
    trust_headers = raw.iloc[header_row, trust_cols].tolist()

    assets_df = raw.iloc[header_row + 1 :, assets_cols].copy()
    trust_df = raw.iloc[header_row + 1 :, trust_cols].copy()

    assets_df.columns = [str(h).strip() for h in assets_headers]
    trust_df.columns = [str(h).strip() for h in trust_headers]

    assets_df = assets_df.dropna(how="all")
    trust_df = trust_df.dropna(how="all")

    # Normalize whitespace.
    for df in (assets_df, trust_df):
        for col in df.columns:
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    return assets_df, trust_df


def _load_sheet3_stride(xlsx_path: Path) -> pd.DataFrame:
    raw = pd.read_excel(xlsx_path, sheet_name="Sheet3", header=None)
    header_row = _find_header_row(raw, "ID")
    headers = raw.iloc[header_row, :7].tolist()
    df = raw.iloc[header_row + 1 :, :7].copy()
    df.columns = [str(h).strip() for h in headers]
    df = df.dropna(how="all")
    for col in df.columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # Normalize header names to stable report-friendly labels.
    rename_map = {
        "Asset": "Asset Affected",
        "Affected Trust Levels": "Trust Levels",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df


def _apply_required_edits(assets_df: pd.DataFrame, trust_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    assets_df = assets_df.copy()
    trust_df = trust_df.copy()

    # Requirement: contextualize ticket state integrity.
    if "Asset" in assets_df.columns and "Description" in assets_df.columns:
        mask = assets_df["Asset"].astype(str).str.strip().str.casefold().eq("ticket state integrity")
        if mask.any():
            assets_df.loc[mask, "Asset"] = "Ticket State Integrity (Available, Reserved, Paid, Used)"
            assets_df.loc[mask, "Description"] = (
                "Lifecycle state machine for tickets: AVAILABLE → RESERVED → PAID → USED (plus REFUNDED for reversals)."
            )

    # Requirement: cross-reference Staff/Admin trust levels to architect entry points.
    # Add a column without altering the original columns.
    alignment_col = "Entry Point Alignment (person1_architect.md)"
    if alignment_col not in trust_df.columns:
        trust_df.insert(len(trust_df.columns), alignment_col, "")

    if "Entity" in trust_df.columns:
        entity = trust_df["Entity"].astype(str)
        staff_mask = entity.str.contains("staff", case=False, na=False)
        admin_mask = entity.str.contains("admin", case=False, na=False) | entity.str.contains(
            "administrator", case=False, na=False
        )

        trust_df.loc[staff_mask, alignment_col] = "Entry Point 1.6 Staff Check-in (Trust Level (4))"
        trust_df.loc[admin_mask, alignment_col] = "Web Gateway (HTTPS) (Trust Level (5)) — admin-only routes (assumed)"

    return assets_df, trust_df


def _tables_in_order(xlsx_path: Path) -> Iterable[Table]:
    assets_df, trust_df = _load_sheet1_assets_and_trust(xlsx_path)
    stride_df = _load_sheet3_stride(xlsx_path)

    assets_df, trust_df = _apply_required_edits(assets_df, trust_df)

    # Keep consistent column order for output.
    assets_cols = [
        "ID",
        "Asset",
        "Description",
        "Associated Trust Level",
        "Sensitivity",
        "Why It Matters (Risk)",
    ]
    trust_cols = [
        "ID",
        "Entity",
        "Description",
        "Trust Level",
        "Capabilities",
        "Risk if Compromised",
        "Entry Point Alignment (person1_architect.md)",
    ]
    stride_cols = [
        "ID",
        "Threat Type",
        "Threat Description",
        "Security Controls",
        "Asset Affected",
        "Trust Levels",
        "Impact",
    ]

    assets_df = assets_df[[c for c in assets_cols if c in assets_df.columns]]
    trust_df = trust_df[[c for c in trust_cols if c in trust_df.columns]]
    stride_df = stride_df[[c for c in stride_cols if c in stride_df.columns]]

    yield Table("Section 5: Assets", assets_df)
    yield Table("Section 6: Trust Levels", trust_df)
    yield Table("STRIDE Threat Analysis (from spreadsheet)", stride_df)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    xlsx_path = repo_root / "Assests_Trust_Level_Stride.xlsx"

    parts: list[str] = []
    tables = list(_tables_in_order(xlsx_path))

    # Section 5
    parts.append(f"## {tables[0].title}")
    parts.append("")
    parts.append(_to_markdown_table(tables[0].df))
    parts.append("")

    # Section 6
    parts.append(f"## {tables[1].title}")
    parts.append("")
    parts.append(_to_markdown_table(tables[1].df))
    parts.append("")

    # STRIDE table (kept within this deliverable; spreadsheet includes it)
    parts.append("### STRIDE Threat Analysis")
    parts.append("")
    parts.append(_to_markdown_table(tables[2].df))
    parts.append("")

    print("\n".join(parts).rstrip() + "\n")


if __name__ == "__main__":
    main()
