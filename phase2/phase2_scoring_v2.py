# phase2_scoring_v2.py
# Inputs:
#   bbb_positive_drugs.csv
#   chembl_drug_mechanism_curated.csv
#   ad_genes_disgenet.csv
#
# Outputs:
#   phase2_scored_drugs_v3.csv
#   phase2_v2_report.txt

import pandas as pd
import re

def norm_name(x: str) -> str:
    if pd.isna(x):
        return ""
    x = str(x).lower()
    x = re.sub(r"\(.*?\)", "", x)
    x = re.sub(r"[^a-z0-9\s]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x

print("🚀 Phase 2 v2 scoring started")

# --------------------------
# 1) Load inputs
# --------------------------
bbb = pd.read_csv("bbb_positive_drugs.csv")
moa = pd.read_csv("chembl_drug_mechanism_curated.csv")
ad  = pd.read_csv("ad_genes_disgenet.csv")

# --------------------------
# 2) Detect BBB drug-name column
# --------------------------
bbb_name_col = None
for c in ["compound_name", "drug_name", "name"]:
    if c in bbb.columns:
        bbb_name_col = c
        break
if bbb_name_col is None:
    raise SystemExit(f"❌ BBB file missing drug name column. Columns: {bbb.columns.tolist()}")

print("BBB name col:", bbb_name_col)

bbb["drug_norm"] = bbb[bbb_name_col].apply(norm_name)

# --------------------------
# 3) Normalize MOA data
# --------------------------
if "drug_name" not in moa.columns:
    raise SystemExit(f"❌ chembl_drug_mechanism_curated.csv missing drug_name. Columns: {moa.columns.tolist()}")

moa["drug_norm"] = moa["drug_name"].apply(norm_name)

# AD gene set
ad_genes = set(ad["gene_symbol"].astype(str).str.strip().tolist())
ad_genes_upper = {g.upper() for g in ad_genes}

# Choose best target identifier: gene symbol if present, else target name
moa["target_gene"] = moa.get("target_gene", "").fillna("").astype(str).str.strip()
moa["target_name"] = moa.get("target_name", "").fillna("").astype(str).str.strip()

moa["target_best"] = moa["target_gene"]
mask_empty = moa["target_best"].eq("")
moa.loc[mask_empty, "target_best"] = moa.loc[mask_empty, "target_name"]

# --------------------------
# 4) Scientific weighting
# --------------------------
HIGH = {"APP", "BACE1", "PSEN1", "PSEN2", "MAPT", "GSK3B", "TREM2", "APOE", "ADAM10", "CDK5"}
LOW  = {"ACHE"}  # keep but downweight

def target_weight(t):
    t = str(t).strip().upper()
    if t in HIGH:
        return 3.0
    if t in LOW:
        return 0.5
    if t in ad_genes_upper:
        return 1.0
    return 0.0

moa["t_upper"] = moa["target_best"].astype(str).str.upper()
moa["w"] = moa["t_upper"].apply(target_weight)

# Keep only rows with any AD-related weight
moa_ad = moa[moa["w"] > 0].copy()

# --------------------------
# 5) Build drug-level features WITHOUT groupby.apply warning
# --------------------------
# num_targets_moa: total unique targets (from ALL moa, not just AD targets)
num_targets_moa = moa.groupby("drug_norm")["t_upper"].nunique()

# ad_weight_sum: sum of weights across AD-related target rows
ad_weight_sum = moa_ad.groupby("drug_norm")["w"].sum()

# ad_hit_targets: list of unique AD targets hit
ad_hit_targets = moa_ad.groupby("drug_norm")["t_upper"].apply(lambda s: ";".join(sorted(set(s))))

features = pd.DataFrame({
    "drug_norm": num_targets_moa.index,
    "num_targets_moa": num_targets_moa.values
}).merge(
    ad_weight_sum.rename("ad_weight_sum"),
    on="drug_norm",
    how="left"
).merge(
    ad_hit_targets.rename("ad_hit_targets"),
    on="drug_norm",
    how="left"
)

features["ad_weight_sum"] = features["ad_weight_sum"].fillna(0.0)
features["ad_hit_targets"] = features["ad_hit_targets"].fillna("")

# --------------------------
# 6) Merge into BBB list
# --------------------------
out = bbb.merge(features, on="drug_norm", how="left")
out["num_targets_moa"] = out["num_targets_moa"].fillna(0).astype(int)
out["ad_weight_sum"] = out["ad_weight_sum"].fillna(0.0)
out["ad_hit_targets"] = out["ad_hit_targets"].fillna("")

# Unified output name
out["drug_name_out"] = out[bbb_name_col].astype(str)

# Normalize by number of targets (avoid promiscuous domination)
out["ad_score_norm"] = out["ad_weight_sum"] / out["num_targets_moa"].clip(lower=1)

# If you have BBB score, include it; otherwise use AD score only
if "bbb_score" in out.columns:
    out["phase2_score_v2"] = 0.6 * out["ad_score_norm"] + 0.4 * out["bbb_score"].fillna(0)
else:
    out["phase2_score_v2"] = out["ad_score_norm"]

out = out.sort_values("phase2_score_v2", ascending=False)

# --------------------------
# 7) Save outputs
# --------------------------
out.to_csv("phase2_scored_drugs_v3.csv", index=False)

top = out.head(30)[["drug_name_out", "num_targets_moa", "ad_hit_targets", "phase2_score_v2"]]

with open("phase2_v2_report.txt", "w", encoding="utf-8") as f:
    f.write(f"Total BBB+ drugs: {len(out)}\n")
    nonzero = (out["phase2_score_v2"] > 0).sum()
    f.write(f"Non-zero Phase2 v2 score: {nonzero} ({100*nonzero/len(out):.2f}%)\n\n")
    f.write("Top 30 candidates:\n")
    f.write(top.to_string(index=False))
    f.write("\n")

print("✅ Saved phase2_scored_drugs_v3.csv")
print("✅ Saved phase2_v2_report.txt")
print("\nTop 30 candidates:")
print(top)
