# 🧠 Alzheimer’s Drug Candidate Prioritization (Hackathon System)

This project is an end-to-end **drug candidate prioritization pipeline** for Alzheimer’s disease.  
It combines:

- **Phase 1:** Blood–Brain Barrier (BBB) screening (already trained/produced)
- **Phase 2:** Mechanistic plausibility scoring using drug–target interactions
- **Phase 3:** Live biomedical literature mining using Europe PMC (public API)
- **Final:** A merged score that ranks candidates for demo and review

> ⚠️ Important: This system **does not claim clinical efficacy**.  
> It produces a **ranked shortlist of candidates** based on mechanistic plausibility + literature evidence.

---

## ✅ What the system outputs

- `final_ranked_candidates.csv`  
  Final ranked list of BBB-positive drugs with:
  - Phase 2 mechanism score
  - Phase 3 literature evidence score
  - Final combined score

- `phase3/outputs/phase3_lit_evidence.csv`  
  Aggregated per-drug literature evidence (signed score, net positivity, model diversity)

- `phase3/outputs/phase3_papers.csv`  
  Extracted paper-level evidence (title, model, direction, outcomes)

---

## 🧩 Repository structure

