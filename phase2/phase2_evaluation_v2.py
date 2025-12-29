import pandas as pd

df = pd.read_csv("phase2_scored_drugs_v3.csv")

print("Total:", len(df))
print("Columns:", df.columns.tolist())

print("\nScore stats:")
print(df["phase2_score_v2"].describe())

nonzero = df[df["phase2_score_v2"] > 0].copy()
print("\nNon-zero:", len(nonzero), f"({100*len(nonzero)/len(df):.2f}%)")

# Detect the display drug column
display_col = None
for c in ["drug_name_out", "drug_name", "compound_name", "name"]:
    if c in df.columns:
        display_col = c
        break

if display_col is None:
    raise SystemExit("❌ No drug name column found to display in phase2_scored_drugs_v3.csv")

print("\nUsing display column:", display_col)

print("\nTop 25:")
print(
    nonzero.sort_values("phase2_score_v2", ascending=False).head(25)[
        [display_col, "num_targets_moa", "ad_hit_targets", "phase2_score_v2"]
    ]
)

print("\nBottom 25 (still non-zero):")
print(
    nonzero.sort_values("phase2_score_v2", ascending=True).head(25)[
        [display_col, "num_targets_moa", "ad_hit_targets", "phase2_score_v2"]
    ]
)
