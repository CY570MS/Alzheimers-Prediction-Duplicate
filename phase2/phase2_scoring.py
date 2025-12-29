# =========================
# Phase 2 Scoring (FIXED)
# =========================

print("🚀 phase2_scoring.py started (with name normalization)")

import pandas as pd
import re

# --------------------------------------------------
# Helper: normalize drug names
# --------------------------------------------------
def normalize_drug_name(name):
    if pd.isna(name):
        return ""
    name = name.lower()
    name = re.sub(r"\(.*?\)", "", name)   # remove parentheses
    name = re.sub(r"[^a-z0-9\s]", "", name)  # remove punctuation
    name = re.sub(r"\s+", " ", name).strip()
    return name

# --------------------------------------------------
# 1) Load CSVs
# --------------------------------------------------
bbb = pd.read_csv("bbb_positive_drugs.csv")
dt  = pd.read_csv("drug_target_interactions.csv")

print("BBB shape:", bbb.shape)
print("Drug-target shape:", dt.shape)

# --------------------------------------------------
# 2) Detect columns
# --------------------------------------------------
# BBB drug column
bbb_name_col = None
for c in ["compound_name", "drug_name", "name"]:
    if c in bbb.columns:
        bbb_name_col = c
        break
if bbb_name_col is None:
    raise ValueError("No drug name column in BBB file")

# Drug-target name column
dt_name_col = "drug_name"
if dt_name_col not in dt.columns:
    raise ValueError("drug_name column missing in drug_target_interactions.csv")

# Target column
target_col = None
for c in ["target_gene", "gene_symbol", "target_name", "target"]:
    if c in dt.columns:
        target_col = c
        break
if target_col is None:
    raise ValueError("No target column found")

print("BBB drug column:", bbb_name_col)
print("DT drug column:", dt_name_col)
print("Target column:", target_col)

# --------------------------------------------------
# 3) Normalize drug names (CRITICAL FIX)
# --------------------------------------------------
bbb["drug_norm"] = bbb[bbb_name_col].apply(normalize_drug_name)
dt["drug_norm"]  = dt[dt_name_col].apply(normalize_drug_name)

# --------------------------------------------------
# 4) Alzheimer target genes
# --------------------------------------------------
alz_genes = {
    "APP","BACE1","PSEN1","PSEN2","ADAM10",
    "MAPT","GSK3B","CDK5","MARK4",
    "TNF","IL1B","IL6","TREM2","CSF1R",
    "APOE","CLU","BIN1",
    "ACHE","GRIN2B",
    "SOD1","SOD2","NFE2L2"
}

# Normalize target names → genes (lightweight)
name_to_gene = {
    "amyloid beta a4 protein": "APP",
    "beta secretase 1": "BACE1",
    "tau protein": "MAPT",
    "glycogen synthase kinase 3 beta": "GSK3B",
    "cyclin dependent kinase 5": "CDK5",
    "tumor necrosis factor": "TNF",
    "interleukin 1 beta": "IL1B",
    "interleukin 6": "IL6",
    "triggering receptor expressed on myeloid cells 2": "TREM2",
    "colony stimulating factor 1 receptor": "CSF1R",
    "apolipoprotein e": "APOE",
    "acetylcholinesterase": "ACHE",
}

def normalize_target(t):
    t = str(t).lower().strip()
    return name_to_gene.get(t, t)

dt["target_norm"] = dt[target_col].apply(normalize_target)

# --------------------------------------------------
# 5) Build drug → target map (NOW WILL MATCH)
# --------------------------------------------------
print("Building drug → target map...")
drug_to_targets = (
    dt.groupby("drug_norm")["target_norm"]
    .apply(lambda s: set(x for x in s if x))
    .to_dict()
)
print("Drug map size:", len(drug_to_targets))

# --------------------------------------------------
# 6) Compute Phase 2 scores
# --------------------------------------------------
rows = []

for _, row in bbb.iterrows():
    drug = row[bbb_name_col]
    drug_norm = row["drug_norm"]

    targets = drug_to_targets.get(drug_norm, set())
    ad_hits = targets.intersection(alz_genes)

    rows.append({
        "drug_name": drug,
        "num_targets": len(targets),
        "num_ad_targets": len(ad_hits),
        "ad_hit_targets": ";".join(sorted(ad_hits)) if ad_hits else "",
        "ad_target_ratio": len(ad_hits) / max(len(targets), 1)
    })

feat = pd.DataFrame(rows)

# --------------------------------------------------
# 7) Final Phase 2 score
# --------------------------------------------------
if "bbb_score" in bbb.columns:
    feat["phase2_score"] = 0.5*feat["ad_target_ratio"] + 0.5*bbb["bbb_score"].fillna(0)
else:
    feat["phase2_score"] = feat["ad_target_ratio"]

feat = feat.sort_values("phase2_score", ascending=False)

# --------------------------------------------------
# 8) Save output
# --------------------------------------------------
feat.to_csv("phase2_scored_drugs_v3.csv", index=False)

print("✅ Phase 2 complete (FIXED)")
print(feat.head(20))
