#!/usr/bin/env python3
"""
postprocess_batch.py — Repair batch extraction outputs (DEC-028 v3 batch fix)
=============================================================================
Restores `source_file` in each record's _meta by joining with id_map_PS.csv /
id_map_SV.csv on the runtime ID, then re-runs block/status enrichment using
block_mapping.csv v3.1 (filename-keyed exact match).

Use this when the batch run produced a v3 xlsx with empty `block`, `block_label`,
`list_order`, `status` columns due to a missing source_file in batch _meta.

Does NOT re-extract anything. Pure file-side reconstruction.

Usage:
    python postprocess_batch.py
    python postprocess_batch.py --xlsx path/to/extraction_SLR_*.xlsx

Author: C. Lambert-Tremblay — UQO 2026
"""

import argparse, json, re, sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# ---- Paths (mirror extract_slr.py defaults) -----------------------------
BASE_DIR = Path(r"C:\Users\ConstanceLambert\Université du Québec en Outaouais"
                r"\Projet de mémoire - NeSy Harmonisation Sémantique - General"
                r"\Maitrise\SLR_thesis\data")
OUTPUT_DIR = BASE_DIR / "extraction_output"


# ---- Helpers (copied from extract_slr.py for standalone use) ------------

def find_block_mapping():
    candidates = [
        OUTPUT_DIR / "block_mapping.csv",
        Path(__file__).parent / "block_mapping.csv",
        Path.cwd() / "block_mapping.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_block_mapping(path):
    df = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False)
    by_fn, by_ay = {}, {}
    for _, row in df.iterrows():
        record = {
            "block": row.get("block", ""),
            "block_label": row.get("block_label", ""),
            "list_order": row.get("list_order", ""),
            "rank": row.get("rank", ""),
            "status": row.get("status", "included"),
        }
        fn = str(row.get("filename", "")).strip()
        if fn:
            by_fn[fn] = record
        ref = str(row.get("short_ref", ""))
        rtype = str(row.get("type", "")).upper()
        tokens = re.findall(r"[A-Za-z]+", ref)
        years = re.findall(r"\b(20[0-9]{2})\b", ref)
        if tokens and years:
            by_ay[f"{rtype}_{tokens[0].lower()}_{years[0]}"] = record
    return by_fn, by_ay


def load_id_map(prefix):
    """Read id_map_PS.csv or id_map_SV.csv → {PS-001: '058_Chen_2024.pdf'}"""
    path = OUTPUT_DIR / f"id_map_{prefix}.csv"
    if not path.exists():
        print(f"  ⚠️  {path.name} not found")
        return {}
    df = pd.read_csv(path, encoding="utf-8-sig", keep_default_na=False)
    return dict(zip(df["id"], df["filename"]))


def find_latest_xlsx():
    """Find the most recent extraction_SLR_*.xlsx in OUTPUT_DIR."""
    candidates = sorted(OUTPUT_DIR.glob("extraction_SLR_*.xlsx"))
    return candidates[-1] if candidates else None


# ---- Repair logic --------------------------------------------------------

def repair(xlsx_path):
    print(f"Reading {xlsx_path.name}...")
    df_a5 = pd.read_excel(xlsx_path, sheet_name="A5_Primary_Studies")
    df_a6 = pd.read_excel(xlsx_path, sheet_name="A6_Surveys")
    print(f"  A5: {len(df_a5)} rows | A6: {len(df_a6)} rows")

    # ---- Step 1: restore source_file from id_map -------------------------
    print("\n[1/3] Restoring source_file from id_map_*.csv ...")
    id_map_ps = load_id_map("PS")
    id_map_sv = load_id_map("SV")
    print(f"  id_map_PS: {len(id_map_ps)} entries | id_map_SV: {len(id_map_sv)} entries")

    # The xlsx column may be called 'source_file' (set by flatten_a5/a6 but empty for batch)
    # We fill it from id_map keyed on 'id'
    if "source_file" not in df_a5.columns:
        df_a5["source_file"] = ""
    if "source_file" not in df_a6.columns:
        df_a6["source_file"] = ""

    n_a5 = df_a5["source_file"].apply(lambda x: bool(str(x).strip())).sum()
    n_a6 = df_a6["source_file"].apply(lambda x: bool(str(x).strip())).sum()
    print(f"  Before fill: A5 source_file populated = {n_a5}/{len(df_a5)}, "
          f"A6 = {n_a6}/{len(df_a6)}")

    df_a5["source_file"] = df_a5.apply(
        lambda r: id_map_ps.get(str(r["id"]).strip(), str(r.get("source_file", "")).strip()),
        axis=1
    )
    df_a6["source_file"] = df_a6.apply(
        lambda r: id_map_sv.get(str(r["id"]).strip(), str(r.get("source_file", "")).strip()),
        axis=1
    )
    n_a5 = df_a5["source_file"].apply(lambda x: bool(str(x).strip())).sum()
    n_a6 = df_a6["source_file"].apply(lambda x: bool(str(x).strip())).sum()
    print(f"  After fill : A5 = {n_a5}/{len(df_a5)}, A6 = {n_a6}/{len(df_a6)}")

    # ---- Step 2: re-enrich block / block_label / list_order / status -----
    print("\n[2/3] Re-enriching block columns via filename exact match ...")
    bm_path = find_block_mapping()
    if not bm_path:
        print("  ❌ block_mapping.csv not found — aborting enrichment.")
        return None
    print(f"  Using {bm_path}")
    by_fn, by_ay = load_block_mapping(bm_path)
    print(f"  Loaded: {len(by_fn)} by filename, {len(by_ay)} by author+year fallback")

    def enrich(df, article_type):
        blocks, labels, orders, statuses = [], [], [], []
        matched_fn, matched_ay = 0, 0
        for _, row in df.iterrows():
            sf = str(row.get("source_file", "")).strip()
            m = by_fn.get(sf, {})
            if m:
                matched_fn += 1
            else:
                # fallback by authors+year
                authors = str(row.get("authors", ""))
                year = str(row.get("year", ""))
                first = re.findall(r"[A-Za-z]+", authors)
                key = f"{article_type}_{first[0].lower()}_{year}" if first and year else ""
                m = by_ay.get(key, {})
                if m:
                    matched_ay += 1
            blocks.append(m.get("block", ""))
            labels.append(m.get("block_label", ""))
            orders.append(m.get("list_order", ""))
            statuses.append(m.get("status", ""))
        print(f"  {article_type}: {matched_fn} matched by filename + {matched_ay} by author+year "
              f"= {matched_fn + matched_ay}/{len(df)}")
        return blocks, labels, orders, statuses

    for tag, df in [("PS", df_a5), ("SV", df_a6)]:
        b, l, o, s = enrich(df, tag)
        # Overwrite existing columns (which were empty after batch)
        df["block"] = b
        df["block_label"] = l
        df["list_order"] = o
        df["status"] = s

    # ---- Step 3: save repaired xlsx --------------------------------------
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = OUTPUT_DIR / f"extraction_SLR_{ts}_REPAIRED.xlsx"
    print(f"\n[3/3] Writing repaired xlsx: {out_path.name}")
    with pd.ExcelWriter(out_path, engine="openpyxl") as w:
        df_a5.to_excel(w, sheet_name="A5_Primary_Studies", index=False)
        df_a6.to_excel(w, sheet_name="A6_Surveys", index=False)
        pd.DataFrame({
            "Metric": ["A.5 count", "A.6 count", "Source xlsx", "Repaired at", "Version"],
            "Value": [len(df_a5), len(df_a6), xlsx_path.name, ts, "v3.1-batch-repair"]
        }).to_excel(w, sheet_name="Summary", index=False)

    # Also write a small summary of what was repaired
    print(f"\n✓ Repair complete: {out_path}")
    print(f"  PS rows with block label: "
          f"{df_a5['block'].apply(lambda x: bool(str(x).strip())).sum()}/{len(df_a5)}")
    print(f"  SV rows with block label: "
          f"{df_a6['block'].apply(lambda x: bool(str(x).strip())).sum()}/{len(df_a6)}")
    print(f"  PS with status='included': {(df_a5['status']=='included').sum()}, "
          f"'standby': {(df_a5['status']=='standby').sum()}, "
          f"'retired': {(df_a5['status']=='retired').sum()}")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Repair batch extraction xlsx")
    ap.add_argument("--xlsx", type=str, default=None,
                    help="Path to extraction_SLR_*.xlsx to repair (default: latest)")
    args = ap.parse_args()

    if args.xlsx:
        xlsx_path = Path(args.xlsx)
    else:
        xlsx_path = find_latest_xlsx()
        if not xlsx_path:
            print(f"❌ No extraction_SLR_*.xlsx found in {OUTPUT_DIR}")
            sys.exit(1)
        print(f"Using latest xlsx: {xlsx_path.name}")

    if not xlsx_path.exists():
        print(f"❌ Not found: {xlsx_path}")
        sys.exit(1)

    repair(xlsx_path)


if __name__ == "__main__":
    main()
