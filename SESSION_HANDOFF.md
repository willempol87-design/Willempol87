# Session handoff — thesis + tool development, [continued from long session]

This file preserves context from a very long working session so a new session can continue without losing state. Read this first, then continue where indicated.

## 1. Thesis structure — status per chapter

Numbering below is the CURRENT, corrected numbering (Ch4 = old Ch4+Ch5 merged, everything after shifted down by 1). Fixing final numbering site-wide is still pending until all chapters are drafted.

1. **Introduction** — NOT written yet, still original bullets.
2. **The Nearshore Environment** — DONE. Wave breaking expanded, tidal influence/wave-current interaction shortened, Bed Morphology reframed around bedrock/mobile-sand governing cases, new paragraph added on breaking-induced longshore currents (cited: Battjes 1974, via Schiereck & Verhagen 2019).
3. **Hydrodynamic Forcing** — DONE. Currents section compressed (Introduction, Tidal Currents, Other Currents incl. longshore current), Waves section compressed (Introduction, Wave Parameters — precise Tp wording confirmed against Schiereck & Verhagen p.~148, Relevance for stability kept). Old 3.3 Wave-Current interaction removed (redundant with Ch2).
4. **Stability Parameters & Criteria** — DONE. Merged old Ch4 (Near-bed Flow Conditions, now an intro section) + old Ch5. Sections: intro, 4.1 Shields, 4.2 Turbulence-based (Hofland 2005, cited via Van Rijn 2019 — NOT a primary source we have), 4.3 Combined Wave-Current (Van Rijn Eq. 5, verified), 4.4 Decision Framework — **REWRITTEN to match Ch5.8's logic** (was inconsistent: old 4.4 said "wave-dominated → Van der Meer" but Ch5.8 says Van der Meer is only a sanity check; also dropped the TKE branch since no implementable formula exists for it). New 4.4 text given in chat, not yet confirmed pasted into document.
5. **Rock Stability Assessment Methods** — DONE, including new 5.7 Rock Density (Deltares Ch.4.4.1.5) and 5.8 Comparative Summary. All 6 method sections verified against source PDFs (Hudson, Van der Meer, Van Rijn, Van Gent & Van der Werf, Herrera & Medina, Deltares HaSPro/RoBeD — including full TOPC/hberm/Bberm equations from the RoBeD deformation model, Eq 20-26, with the Δcable notation clash flagged: in RoBeD, Δ = cable offset, NOT relative density as used elsewhere).
6. **Scour** — DONE. Fixed 3 duplicate "The Scour Process" headings → 6.1 The Scour Process, 6.2 Scour Around Subsea Cables, 6.3 Scour and Berm Stability, 6.4 Scour Mitigation Approaches, 6.5 Anchor and Trawling Protection (Context) — includes horseshoe-vortex correction (not applicable to low sloped berms, only piles/cylinders) and the "per-project risk assessment, not universal minimum" nuance for anchor/trawl figures.
7. **Design Framework & Computational Approach** — NOT written yet (still original bullets: 7.1 Input Parameter Space, 7.2 Core Design Formulae, 7.3 Failure Criteria & Damage Levels, 7.4 Validity Ranges, 7.5 Sensitivity Analysis). Gap analysis done (see section 3 below) — needs a new 7.2 "Method Selection Logic" subsection and a new "Output & Trade-off" subsection that don't exist yet. Also needs the explicit MTOC/boundary-condition-check text (see section 3).
8. **Knowledge Gaps & Research Questions** — NOT written yet.

**Note on Scour vs old plan:** original plan (very early in session) was to merge Scour+anchor/trawling into a brand new "Design Requirements & Boundary Conditions" chapter. This was superseded — user preferred keeping original chapter numbers/titles largely intact (minimal-diff philosophy), so Scour stayed its own chapter with anchor/trawling as 6.5 within it.

## 2. Reference material fixed/added to repo

- `papers/` — all 5 core PDFs renamed per convention (VanRijn_2019_CriticalRockMovement.pdf, VanGent_VanderWerf_2014_ToeStability.pdf, HerreraMedina_2015_ToeBerm_ShallowSteep.pdf, Deltares_2023_HaSPro_Handbook.pdf, Schiereck_Verhagen_2019_BedBankShoreProtection.pdf) + `_extracted_text/`.
- **IMPORTANT FIX**: Schiereck & Verhagen's extracted text was corrupted (font-encoding issue in the PDF gave garbled pdftotext output). Re-extracted the full 435-page book via OCR (pdftoppm + tesseract), replaced the file, committed. Now readable and used for verification (confirmed 0.88 breaker index value, Hs/Tp definitions, turbulence/boundary layer content, Hudson/Van der Meer details, horseshoe vortex context, all correct).
- New source found and used: **Van Kessel & Stam (2010), "The Lights Go Out", SubOptic 2010** (Van Oord) — anchor/trawling protection rules of thumb, 0.5m cover baseline, dragging anchor berm sizing example. Cited in Ch6.5. PDF was uploaded by user, not saved into papers/ folder yet (should be added if referenced formally).
- New source found (just now, end of session): **DNV-RP-F109, "On-bottom stability design of submarine pipelines, cables and umbilicals", Edition May 2021, Section 2.6 "Load combinations"**. This is an authoritative, citable justification for the 10yr/100yr wave-current return period combination approach discussed at length (see section 4). Key content: 100-yr design condition = worse of [100yr wave + up to 10yr current] or [10yr wave + up to 100yr current]; for temporary phases <12 months, seasonal 10yr/1yr combinations apply instead. Also notes: check lower current velocities too, since combined loading is non-linear in current/wave velocity ratio, sometimes a smaller current is more conservative. **This should be added as a citation in Chapter 3 (Currents) or Chapter 7, and used to justify why the colleague's existing code's 10/100 combination logic is legitimate.**
- Also read in full: NKT "Cable Burial and Protection Plan" (Shetland HVDC Link) — gave DOC/DOL/DOT/TOC definitions, rock berm design standards (top width 1m, slope 1:3/1:4, min DOC 0.6m, min berm height 0.3m), EN-13383-1 rock material standard, water depth reduction table. Not yet placed into the thesis (was offered for Ch1 terminology / Ch5-6 / Ch7 context but no final decision made).

## 3. Open technical/architecture issues flagged (not yet resolved)

1. **The core open question (needs supervisor input, already in project scope doc):** no common scale exists to convert between r (Van Rijn), Nod (Van Gent/Herrera & Medina), and deformation class (Deltares). Three options drafted for user to bring to Elisabeth/Shamsa/Alessandro: (1) treat sizing decision and Deltares finalization as fully separate decisions, (2) propose own approximate mapping, clearly flagged as unvalidated, (3) only connect methods where a link already makes sense (Van Rijn→Deltares yes, Herrera & Medina→Deltares no). User has a Monday meeting planned to discuss this.
2. **MTOC boundary-condition check** — agreed text (not yet in the document): the hydraulically-required geometry from Ch7 calculations must be compared against project MTOC (Ch6.5), whichever is larger governs, tool must state which one governed. Not yet in Ch7 draft.
3. **Deltares' own mobility-limit tables are pile-specific, not for cable berms** — flagged in Ch5.8/5.6, the "mobility threshold ≈0.95" originally in the comparison table was wrong (came from a monopile Dpile=8m table), corrected to "MOBthresh (case-specific, no fixed default)".
4. **Colleague's existing Van Rijn/Deltares code — bugs found during review** (full code was shared, extensively reviewed line by line):
   - No method-selection logic at all — runs Van Rijn unconditionally on every point regardless of seabed type/slope/breaking (direct real-world example of the thesis's own stated problem).
   - `r` (damage reduction coefficient) and `gstr` (turbulence/structure factor) hardcoded as constants, not adjustable per project.
   - **UPDATE (this session, code + real sample data obtained and traced through, see `code/` folder):** the code is now saved in the repo at `code/nkt_stability_tool_original.py`, with sample input data at `code/sample_data/` and a standalone repro script at `code/bug_analysis_orbital_velocity.py`.
     - **Confirmed real bug, root cause identified**: the wave orbital velocity calculation (`Uwc1`/`Uwc2`, both combo blocks) wraps the sinh() argument in an extra `np.radians()` call: `sinh(radians(2*pi*WL/LSc))`. That argument (kh = 2·π·h/L) is already a dimensionless ratio, not a degree-based angle, so the conversion is wrong. Traced with a real data point (point_ID 37.919, Hs=3.86m, Tp=8.8s, h=18.1m): code-as-written gives Uw ≈ 68.6 m/s (physically impossible), the standard linear-wave-theory formula without the erroneous wrap gives Uw ≈ 0.97 m/s (realistic). **Factor ~71x**, confirmed numerically, reproducible via `code/bug_analysis_orbital_velocity.py`.
     - **Retracted**: an earlier suspicion this session that the critical-Shields formula (`Tetacrshic1` etc., missing a ×1.2 term compared to the Deltares HaSPro Eq. A.6 / Soulsby form) was a bug turned out to be wrong — checked directly against Van Rijn (2019) Eq. 3 (`papers/VanRijn_2019_CriticalRockMovement.pdf`, p.3, verified visually) which uses exactly `0.3/(1+D*) + 0.055[1-exp(-0.02D*)]`, **no 1.2 factor**. The code correctly follows Van Rijn (2019), not HaSPro/Soulsby directly. This part of the code is fine.
     - **Conceptual concern (not fully resolved)**: `Hydroberm['TSh']` is Van Rijn's θcr (critical/threshold Shields parameter for the rock's own resistance to motion), which then gets rescaled into `TSH` and fed into the Deltares RoBeD reshaping formula (`T = 6*TSH**2 + 50*TSH + 2.4`). But HaSPro's own formula expects θ, the actual applied mobility number under design load (see their worked example, Appendix C.5: θ=0.014 computed from real shear stress, not a threshold value). θcr and θ are different quantities in HaSPro's own notation. Whether this conflation matters in practice is unclear until the orbital-velocity bug above is fixed first.
     - **Revised view on 6 vs 6000**: given the ~71x velocity inflation bug feeds into every downstream quantity (shear stress ∝ Uw², then D50, then TSH), the working hypothesis now is that "6" may have been an ad-hoc adjustment to compensate for absurdly large numbers caused by the velocity bug, rather than a deliberate alternate convention. **Recommended next step (message drafted for Shamsa, see section 6): fix the orbital velocity formula first, then re-check whether 6000 (the published HaSPro coefficient) gives sensible results with corrected velocities.** Not yet done with real project data, still open.
   - Duplicate/dead imports (token, xml.etree, sympy, array, math, csv unused), a variable `in3` silently overwritten and its first definition lost, inconsistent DataFrame construction patterns, no iteration cap on convergence loops, magic numbers with no explanation, hardcoded file paths bypassing its own GUI file-picker.
   - The 10yr-wave/100yr-current + 100yr-wave/10yr-current combination logic (take the governing one) is validated as legitimate practice, not a bug — confirmed by DNV-RP-F109 (see section 2).

## 4. New tool being built from scratch — progress

Following a "classify first with minimal raw data, then only ask for what the selected method needs" philosophy (explicitly preferred by user over "collect everything upfront"). Functions written so far (in chat only, not yet saved to a .py file in the repo):

```python
def classify_slope(slope_ratio):
    # Herrera & Medina's steep-slope method was validated specifically for m = 1/10
    if slope_ratio >= 0.1:
        return "steep"
    else:
        return "mild"

def classify_seabed(soil_type):
    # Only bedrock and mobile sand are in scope for this thesis (Chapter 2). Clay etc. explicitly rejected.
    if soil_type == "bedrock":
        return "bedrock"
    elif soil_type == "sand":
        return "mobile_sand"
    else:
        raise ValueError(f"Soil type '{soil_type}' is out of scope for this tool.")

def select_method(seabed_type, natural_slope, is_breaking):
    # current velocity deliberately NOT a factor here (Van Rijn+Deltares run together on sand regardless of current)
    if seabed_type == "bedrock":
        if natural_slope == "steep" and is_breaking:
            return "herrera_medina"
        else:
            return "van_gent"
    elif seabed_type == "mobile_sand":
        return "van_rijn_and_deltares"
    else:
        raise ValueError("Unknown seabed_type: " + str(seabed_type))

def required_inputs(method):
    requirements = {
        "herrera_medina": ["Hs0", "Tp", "water_depth_at_toe"],
        "van_gent": ["Hs", "Tm_minus_1_0", "water_depth_at_toe", "berm_width", "berm_thickness", "roughness"],
        "van_rijn_and_deltares": ["Hs", "Tp", "water_depth", "current_velocity", "cable_diameter", "MTOC", "top_width"],
    }
    return requirements[method]
```

Breaking check used: `is_breaking = Hs > 0.88 * water_depth` (derived, never asked as direct input).

**Three-phase architecture (user's own idea, validated as good, with honest caveats attached):**
- Phase 1 — obtain candidate rock size (Hudson, Van der Meer, Van Rijn, Van Gent all belong here — note: for these 4, "Phase 1" and "Phase 2" are really the same formula run once vs. run across a sweep, not fully separate steps).
- Phase 2 — compare rock size against damage level, human decision point (trade-off table/graph, Dn50 vs slope vs damage). Herrera & Medina lives ENTIRELY here since it has no direct Dn50-solving form, only a candidate-size-in/damage-out search.
- Phase 3 — finalize with Deltares RoBeD (needs the unresolved r/Nod/deformation-class mapping from issue #1 above before this can connect cleanly to Phase 2's output).

Still missing from the code: the actual formula bodies (Van Rijn's full iterative D50 solve incl. wavelength convergence loop was sketched with a placeholder `wavelength()` function not yet written; Herrera & Medina, Van Gent, Deltares formulas not yet coded at all, though all are documented with exact equations — see section 5).

## 5. Reference deliverables already created (files, not just chat text)

- `/tmp/.../scratchpad/Rock_Stability_Methods_Comparison.docx` — standalone Word file (not the main thesis doc) with Table 1 (method comparison), Table 2 (decision guide), and full formula + variable tables per method, styled consistently. Sent to user as a file twice (updated between sends).
- `/tmp/.../scratchpad/tool_pipeline_v3.png` — corrected flowchart (classify → method selection incl. fixed sand-branch logic → per-method required data → validity check → damage level → trade-off split by density with embedded example graph → justification text → output). Sent to user, this is the presentation-ready version for his boss.
- `/tmp/.../scratchpad/example_tradeoff_graph.png` — the example Dn50-vs-slope trade-off graph embedded in the flowchart above.
- Email drafts written for: (1) presenting the pipeline setup to his boss (sent as chat text, not confirmed sent), (2) to Shamsa about the 6 vs 6000 Deltares formula discrepancy — this thread is ACTIVE, see section 6.

**Note:** all of these are scratchpad files (session-specific temp storage) except the papers/ folder and the OCR fix, which are committed to the git repo on branch `claude/file-access-question-hhu7j7`. If the scratchpad files are needed in a new session, they may not persist — regenerate from the scripts described above if missing (`build_comparison_doc.py`, `add_formula_tables.py`, `build_flowchart_v3.py`, `build_example_graph.py`, all were written to the scratchpad and could be lost between sessions).

## 6. Active thread: message to Shamsa (NKT supervisor)

Status (this session): (b) is now done, code obtained in full and traced through with a real Hydroinput data point, see updated section 3 point 4 above. Root cause found: an extra `np.radians()` wrap on an already-dimensionless sinh() argument in the orbital velocity formula, inflating Uw by ~71x. Draft message prepared for Shamsa (not yet confirmed sent) explaining this and proposing to fix the velocity formula first, then re-test with the published 6000 coefficient:

> Hi Shamsa,
>
> Following up on the 6 vs 6000 question in the RoBeD berm geometry formula: I think I found the actual root cause.
>
> There is a separate bug in the wave orbital velocity calculation (`Uwc1`/`Uwc2`), an extra `radians()` conversion is applied to the sinh() argument, which is already a dimensionless ratio (2·π·h/L) and should not be converted. I tested this with a real data point (Hs=3.86m, Tp=8.8s, h=18.1m) and the bug makes the orbital velocity come out around 70 times too large (68.6 m/s instead of a physically realistic 0.97 m/s).
>
> My hypothesis is that this is what led to using 6 instead of the published 6000 in the berm geometry formula. With velocities inflated by ~70x, using the correct 6000 coefficient would have produced obviously absurd results, so 6 may have been an ad-hoc adjustment to get sane-looking numbers, rather than a deliberate or correct choice.
>
> Proposed next step: fix the orbital velocity formula first (remove the extra `radians()` call), rerun with realistic velocities, and then check whether the formula works correctly again with the published 6000 coefficient.
>
> Happy to walk through the calculation if useful.

Next step when resumed: confirm whether this was actually sent, and follow up once Shamsa/the code's author responds, particularly on the still-open conceptual question (θcr vs θ, see section 3 point 4) and on getting the fix tested against real project output.

## 7. Working style agreements established this session (important, apply everywhere)

- **No em-dashes (—) or semicolons (;) anywhere** in thesis text or messages meant to be sent externally — user finds this "too AI-sounding." Use periods/commas/rephrasing instead.
- **User writes thesis prose himself.** For thesis chapters: I give tips/direction/what-needs-fixing, not full paragraphs, unless he explicitly asks for full text (he has both ways at different points — always check current preference at the time). For brand new sections with no existing notes, he drafts first, I refine after.
- I should push back / keep flagging real errors even after one round, not drop it after mentioning once.
- For code and Python-lesson content: direct collaborative writing together is fine (different from thesis-prose rule), but should stay simple/well-commented, "easy enough that any colleague at NKT could use it," and he wants to understand every line, not just receive finished code.
- Ask user's classify-first-then-required-fields architecture preference was self-derived by him and is correct — always keep raw measured numbers as input, never ask users to pre-classify into categories (slope ratio not "steep"/"mild", soil type from survey not invented labels, current velocity not "present y/n").
- When verifying formulas/facts against PDFs, be explicit about confidence level — flag clearly when something is "confirmed against clean source text" vs. "OCR was ambiguous, verify directly against the PDF image before use."
- Never edit the user's actual Word thesis document directly — only type text in chat for him to paste, or create clearly-separate reference files (Word docs, images) when he asks for those as deliverables.

## 8. Immediate next steps when resuming

**Done this session** (new session, continued from this handoff): DNV-RP-F109 (2021) obtained and fully read, added as a cited source in Ch2.2 (breaking/validity criterion + wave asymmetry mechanism), Ch2.3 (seabed mobility criterion), Ch3.1 (§2.6 load combinations, replacing the old "kept open" sentence), and Ch3.2 (§3.3 wave directionality/spreading, plus a Hs vs Hm0 precision fix sourced from Schiereck & Verhagen Eq. 7.36-7.38). Item 6 below is therefore done. The colleague's stability code was obtained in full this session and is now saved at `code/nkt_stability_tool_original.py` (+ `code/sample_data/`, `code/bug_analysis_orbital_velocity.py`), and traced through with real data: found a confirmed ~71x orbital-velocity bug (spurious `np.radians()` wrap, see section 3 point 4), retracted an earlier false alarm about the critical-Shields formula (code correctly follows Van Rijn 2019 Eq. 3, not HaSPro), and drafted (not yet confirmed sent) a message to Shamsa about it (section 6). Item 5 below is thus substantially advanced but not closed.

A broader "what would my professor flag" review was also done this session. Findings, with user's stated priority (done now vs. later):
- Ch2.1: literal `(Figure x)` placeholder for the three-zone diagram — user: later.
- Ch2.2: wrong cross-reference `(Chapter 6)` should be `(Chapter 5)` (only inconsistent one found, rest checked and correct) — user: **done**.
- Ch8: a bare, uncited ResearchGate URL at the end of the chapter — user: later.
- Ch1 Introduction still bullet-only, no explicit research questions — user: later.
- Ch7 still mostly outline/notes, not written prose — user: later.
- Ch8 ends with "I have to formulate the research questions" instead of actual RQs, and the r/Nod/deformation-class question is presented as 3 open options with no decision — user: later.
- MTOC boundary-check text still not in Ch7 — user: later.
- Sitewide chapter-numbering consistency pass — user: later.
- Data confidentiality statement for NKT route data — user: later.

Remaining next steps:
1. Confirm whether Ch4.4 rewrite and MTOC-check text actually got pasted into the user's document (last known state: given in chat, not confirmed, still open from before this session).
2. Write Chapter 7 (Design Framework & Computational Approach) properly — needs new "Method Selection Logic" subsection, needs the MTOC boundary check text, needs the actual formulas restated from the reference Word doc, needs Failure Criteria updated for all 6 methods (not just 3), needs r/Nod/deformation-class open question flagged explicitly in text.
3. Write Chapter 1 (Introduction) and Chapter 8 (Knowledge Gaps) — not started yet, including actual research questions (currently just a to-do note in Ch8).
4. Resolve or bring back a supervisor decision on the r/Nod/deformation-class mapping question.
5. Follow up on the Shamsa message once sent and once she/the code author responds, particularly on the θcr-vs-θ conceptual question (section 3 point 4) and on testing the orbital-velocity fix against real project output.
6. ~~Add DNV-RP-F109 as a formally cited source~~ — done this session (Ch2.2, Ch2.3, Ch3.1, Ch3.2).
7. Continue building the actual Python tool: write `wavelength()`, the full `van_rijn_d50()`, then Herrera & Medina/Van Gent/Deltares formula functions, using the verified equations already documented in the reference Word doc. Note the colleague's code (now in `code/`) already has a working, Van-Rijn-based D50 iterative solver structure (once the orbital-velocity bug is fixed) that could inform this.
8. Work through the remaining "professor will flag" items above once the user decides to prioritize them (see list above for what's outstanding).
9. Ch4.2 (Turbulence-based Parameters) was checked for DNV additions this session: no relevant content found in DNV-RP-F109, no change made.
