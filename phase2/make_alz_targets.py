import pandas as pd

alz_targets = [
    "APP","BACE1","PSEN1","PSEN2","ADAM10",
    "MAPT","GSK3B","CDK5","MARK4",
    "TNF","IL1B","IL6","TREM2","CSF1R",
    "APOE","CLU","BIN1",
    "ACHE","GRIN2B",
    "SOD1","SOD2","NFE2L2"
]

pd.DataFrame({"target_gene": alz_targets}).to_csv("alzheimers_targets.csv", index=False)
print("✅ Saved alzheimers_targets.csv")
