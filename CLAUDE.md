# MSc Thesis — Hydraulic Stability Methods for Rock Protection of Subsea Cables (NKT / TU Delft)

This folder is the working home for Willem Pol's MSc thesis (Sustainable Ocean and Coastal Engineering).
Internship at NKT (Rotterdam). Supervisors: Elisabeth Sondenaa & Shamsa (NKT), Dr. Alessandro Antonini (TU Delft).

## How to work with me
- **The thesis is written in English (Microsoft Word).** Use the `docx` skill for any thesis-document work.
- **Willem communicates in Dutch.** Reply in Dutch unless asked otherwise; keep thesis *content* (text, tables, figures) in English.
- Don't start writing/producing unless asked — Willem prefers to set direction first, then execute together.
- When citing the source papers, read them from `papers/` (or the faster pre-extracted text in `papers/_extracted_text/`).

## Folder layout
- `papers/` — the 5 core reference PDFs + `_extracted_text/` (plain-text extractions for fast reading)
- `data/` — NKT route data, measurement data
- `code/` — Python stability tool + sensitivity analysis
- `figures/` — plots, diagrams
- `Phyton/` — Willem's earlier Python work (pre-existing)
- `NKT Liturature Research.docx` — the live literature review / thesis draft (do NOT move without asking)

## The 5 core sources (in `papers/`)
- `VanRijn_2019_CriticalRockMovement.pdf` — Shields-based D50 for bed protection under current ±waves; coeff. r (damage), γstr, α(ks). Only method covering combined wave+current on a bed/berm.
- `VanGent_VanderWerf_2014_ToeStability.pdf` — breakwater toe stability; char. orbital velocity û; damage Nod; berm geometry (Bt, tt); slopes 1:1.5 & 1:2; waves only.
- `HerreraMedina_2015_ToeBerm_ShallowSteep.pdf` — toe berm in very shallow water on steep (m=1/10) bottom, breaking waves; Eq.12 → Nod; emerged & submerged.
- `Deltares_2023_HaSPro_Handbook.pdf` — state-of-the-art offshore; external/interface/flexibility (+NID); Ch.5 cable berms + RoBeD deformation model.
- `Schiereck_Verhagen_2019_BedBankShoreProtection.pdf` — textbook basis (Shields, breaking waves, filters, turbulence, combined wave-current shear).

## Locked scope (agreed with NKT supervisors)
- **Object:** free-standing rock berm covering the cable (not a breakwater toe). Toe formulas are assessed for applicability.
- **Seabed types, split into two cases:** (1) bedrock and (2) mobile sandy seabed (berm on sand mainly at crossings/obstacles where burial is impossible).
- **Loading:** waves governing (Hs, Tp, wave direction — available from NKT route data); include wave-breaking zone where relevant; current/combined kept open.
- **Goal:** smallest feasible Dn50 at controlled damage; AVOID overdesign. Show all methods side by side AND state which method per situation.
- **Rock density = explicit design variable:** Δ=(ρs−ρw)/ρw, presets normal 2650 vs high 3000 kg/m³ (compare Dn50 & tonnage; sensitivity candidate).
- **Anchors/trawling:** context/boundary condition only (CIRIA ~0.5 m min cover, DNV/CarbonTrust); not computed by default to avoid overdesign.
- **Layers:** armour + ≥1 underlayer (~22–25 mm) to protect cable from dropped stones → interface stability in scope.
- **Out of scope:** settlement in soft subsoils.
- **Data/validation:** only Willem's supplied datasets + NKT route data; limited validation described honestly (possible follow-up study).

## Deliverables
- Python tool: applies the right method per situation, optimizes Dn50, warns when inputs fall outside each method's validity range.
- Sensitivity analysis (Sobol and/or Morris).
- Next step requested by supervisors: develop Ch.5 & Ch.6, especially a comparison table (which method/which situation, which damage criterion, which inputs per formula).

## Open design question to resolve
Methods output different quantities (D50 vs Nod vs deformation class) with different damage definitions. Proposed common axis: required Dn50 at an agreed damage level; mapping r ↔ Nod ↔ deformation class still to be agreed with supervisors.
