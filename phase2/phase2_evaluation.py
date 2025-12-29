# ==============================
# Phase 2 Evaluation Script
# ==============================
# Input:
#   phase2_scored_drugs_v3.csv
#
# Purpose:
#   Sanity-check and evaluate Phase 2 scoring
# ==============================

import pandas as pd

print("🔍 Phase 2 evaluation started")

# ------------------------------
# 1) Load Phase 2 output
# ------------------------------
df = pd.read_csv("phase2_scored_drugs_v3.csv")

print("Total drugs:", len(df))
print("Columns:", df.columns.tolist())

# ------------------------------
# 2) Basic score distribution
# ------------------------------
print("\n📊 Phase 2 score distribution:")
print(df["phase2_score"].describe())

# ------------------------------
# 3) How many drugs scored > 0?
# ------------------------------
num_nonzero = (df["phase2_score"] > 0).sum()
total = len(df)

print("\n🔢 Non-zero Phase 2 scores:")
print(f"{num_nonzero} / {total} drugs ({100*num_nonzero/total:.2f}%)")

# ------------------------------
# 4) Inspect top Phase 2 candidates
# ------------------------------
print("\n🏆 Top Phase 2 candidates (non-zero scores):")

top_hits = df[df["phase2_score"] > 0][
    ["drug_name", "num_targets", "num_ad_targets", "ad_hit_targets", "phase2_score"]
].sort_values("phase2_score", ascending=False)

print(top_hits.head(20))

# ------------------------------
# 5) Inspect lowest-ranked drugs
# ------------------------------
print("\n⬇️ Lowest-ranked drugs (should be irrelevant):")

print(
    df.sort_values("phase2_score", ascending=True).head(20)[
        ["drug_name", "num_targets", "num_ad_targets", "phase2_score"]
    ]
)

# ------------------------------
# 6) Enrichment test (key metric)
# ------------------------------
has_ad = df["num_ad_targets"] > 0

mean_with_ad = df[has_ad]["phase2_score"].mean()
mean_without_ad = df[~has_ad]["phase2_score"].mean()

print("\n📈 Enrichment check:")
print("Mean score (AD targets):", mean_with_ad)
print("Mean score (no AD targets):", mean_without_ad)
print("Difference:", mean_with_ad - mean_without_ad)

# ------------------------------
# 7) Weak supervision check
# ------------------------------
known_ad_drugs = {
    "Donepezil",
    "Memantine",
    "Rivastigmine",
    "Galantamine"
}

df["rank"] = df["phase2_score"].rank(ascending=False, method="min")

known_hits = df[df["drug_name"].isin(known_ad_drugs)][
    ["drug_name", "phase2_score", "rank"]
]

print("\n🧠 Known Alzheimer drugs ranking:")
if len(known_hits) == 0:
    print("None of the known AD drugs were present in the dataset.")
else:
    print(known_hits)

print("\n✅ Phase 2 evaluation complete")
