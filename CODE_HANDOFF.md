# CODE HANDOFF - rock berm sizing tool

Read this first in a fresh session. It captures the code plan and every decision made
recently, so the new session knows what to do and how to go from the current code to
the next code. Willem communicates in Dutch, the thesis is written in English.

## 0. Decisions from the latest session (these steer everything)
- BUILD DIRECTION: keep improving the colleague tool `code/nkt_stability_tool_fixed.py`,
  reusing its working Van Rijn sizing and Deltares RoBeD geometry. Do NOT rebuild
  everything from scratch. The from-scratch file `code/nearshore_rock_tool.py` (Part 1)
  is the reference for the classification, decision tree and validity-gate logic.
- INTERACTION: terminal, output-first, one route point (KP) at a time.
  OPEN POINT to clarify with Willem first: the colleague tool is a customtkinter GUI,
  which conflicts with "terminal". Likely intent is to reuse the colleague tool's
  calculation core (Van Rijn solve, RoBeD geometry, CSV I/O) but drive it with the
  clean terminal, output-first flow and the method selection. Confirm before big work.
- BUILD ORDER: (1) the minimal rock-size branch fully (sizing + validity + output for
  2650 and 3000 kg/m3), then (2) the Nod branch, then (3) the RoBeD geometry and the
  sizing-to-geometry coupling.

## 1. Project and files
- MSc thesis (NKT / TU Delft): hydraulic stability methods for rock berms protecting
  unburied subsea cables in the nearshore. Repo: willempol87-design/Willempol87,
  work branch: claude/python-willempol87-data-bhbeb7.
- code/nkt_stability_tool_fixed.py  -> colleague tool, the BASE to improve.
- code/nearshore_rock_tool.py       -> new framework Part 1 (classification, decision
  tree, validity gates). Reference for the logic, no formulas yet.
- code/sample_data/                 -> Hydroinput_sample.csv, RockD50_sample.csv.
- docs/writing_notes_next_week.md    -> source-verified findings (Schiereck etc.).
- docs/Rock_Stability_Methods_Verified.docx -> verified method comparison with sources.
- papers/ and papers/_extracted_text/ -> the 5 core sources plus CIRIA C683 chapter 5
  ("KennisWaterbank Hoofdstuk5.pdf" in the repo root is CIRIA C683) and DNV-RP-F109.

## 2. The framework (output-first, per KP)
Pipeline per KP: inputs by discipline -> classify -> select method + check validity ->
size (stage 1) -> geometry (stage 2) -> candidate berms as a trade-off.

Three goals: A minimal rock size (Dn50), B damage number Nod, C berm geometry.

Decision tree for goal A (strongest discriminator first):
- significant current           -> Van Rijn (only combined wave+current method)
- no current, mobile sand        -> Van Rijn (bed protection on a mobile bed)
- bedrock, waves not breaking    -> Van der Meer (+ Hudson as a rough check)
- bedrock, waves breaking        -> Van Gent and Van der Werf (breaker zone)
- steep bedrock + breaking       -> Herrera and Medina (Nod branch), no size method valid
Every selected method is checked against its validity range. Out of range is flagged
with the reason, never silently used.

Classification thresholds (adjustable constants, reported with every result):
- current significant if uc > 0.2 m/s
- steep seabed if slope >= 1:10 (Herrera m = 1/10)
- breaking if Hs > BREAKING_INDEX * h, with BREAKING_INDEX = 0.5  (see fix in section 5)
Keep two slopes separate: seabed slope (from survey) vs berm side slope cotalpha (design).

## 3. What the colleague tool does, and what still needs work
Van Rijn sizing (the in1/in2 solve): computes the threshold D50 from the Shields
approach with the damage coefficient r and the combined wave-current shear TBCW.
This is genuine Van Rijn. Keep it.

Already fixed in nkt_stability_tool_fixed.py:
- orbital velocity: removed the spurious np.radians() on the sinh() argument (was ~71x)
- TSH is now the applied Shields on the berm: theta = TBCW / ((rho_s - rho_w) * g * D50)
- RoBeD coefficient 6 -> 6000 (verified: handbook Eq. 20)
- soil-type test fixed (the `== 'x' or 'y'` always-True bug)
- the Van Rijn threshold D50 is now written to an output sheet

Still to do / restructure:
- REMOVE the Van Rijn + Nod mixing. The berm-geometry part computes a toe damage number
  Nod with the Muttray (2013) form (0.58 - 0.17*..)^3 * Ns^3 and filters candidates by a
  user "Maximum of Nod". That mixes Van Rijn (damage via r) with a toe-berm Nod in one
  calculation, which is exactly the apples-with-pears problem the thesis is about.
  Keep the methods separate.
- ADD method selection (the decision tree). The colleague tool runs Van Rijn on every
  point regardless of situation.
- ADD validity gates and honest out-of-range flagging.
- ADD breaking classification (BREAKING_INDEX = 0.5).
- REPLACE the berm-height formula HB = abs(1 - TSH/T0) * WL / 6. It is dimensionally
  inconsistent (mixes a Shields number with a shear stress) and is not in the handbook.
  Use the RoBeD TOPC procedure instead (section 5 below).
- Note: TBCW is evaluated at the solved-rock roughness, so using it for a very different
  candidate stone is a first-order approximation of the shear. Good enough for sizing.

## 4. Damage handling (agreed)
- The damage / accepted mobility is chosen ONCE, in the sizing step.
- In the geometry step Deltares PREDICTS the reshaping (Bberm/hberm = f(theta)); it does
  NOT ask for a second damage number. So damage is never counted twice.
- The berm is then dimensioned (TOPC) so that after the predicted reshaping the cover
  over the cable stays above the minimum.
- For comparing methods fairly, use one fixed reference damage. For the final design the
  damage is a free, client-chosen variable, producing a set of candidate berms.

## 5. Verified formulas and values (checked against the sources)
Van Rijn (2019):
- theta_cr = r * 0.05, r in 0.4 to 1.0 (r is the damage level)
- combined shear tau_cw = tau_c + tau_w (Van Rijn Eq. 5), tau computed in the tool as TBCW
- validity: D50 = 0.03 to 3 m, horizontal or mild slope, roughness ratios
  h/(alpha*D50) and Aw/(alpha*D50) in 10 to 300, and D50 is the sieve size, D50 ~ 1.2*Dn50

Combined wave-current angle (optimisation lever):
- tau_cw = sqrt( (tau_c + tau_w*cos(theta))^2 + (tau_w*sin(theta))^2 ),
  theta = angle between current and wave direction
  (DNV-RP-F109 2021 Section 8.4.2.3, Soulsby 1997; also Schiereck and Verhagen 2019
  Section 7.2, after Bijker 1967, Figure 7-8)
- For a BOTTOM PROTECTION the maximum shear governs and it is angle dependent (highest
  when waves and current are aligned). The roses give the angle -> a smaller stone when
  they are not aligned. Needs a defensible alignment rule (annual vs seasonal rose).

Deltares RoBeD (2023), the geometry step:
- Bberm/hberm = 6000*theta^2 + 50*theta + 2.4 (Eq. 20, after Roulund et al. 2018b)
- TOPC procedure (Eq. 21 to 26) with inputs WTOP (top width), alpha (side slope 1:alpha),
  MTOC (min cover), Dcable, and Delta_cable (= Dcable for surface-laid, = ZDOL - ZSBL for
  buried). theta is the combined wave-current Shields at the ambient seabed.
- valid in the reshaping regime; complete wash-away above theta ~ 0.06; MOBthresh = 0.95;
  perpendicular wave-current assumed; offshore calibrated (flag for nearshore use).

Breaking criterion (FIX):
- BREAKING_INDEX for Hs = 0.5, NOT 0.88. 0.78 to 0.88 is the individual-wave breaker
  index; for the significant wave height the depth limit is Hs/h ~ 0.4 to 0.5
  (Schiereck and Verhagen 2019, Section 7.3.1). Change BREAKING_INDEX in
  nearshore_rock_tool.py, and add the same logic to the colleague tool.

## 6. Safety floors (never crossed by any optimisation)
- wash-away: theta > ~0.06 -> the berm flattens completely, require a larger stone
- minimum layer thickness ~ 2 to 3 * Dn50 (a real rock layer)
- interface / winnowing on sand: installed berm height >= 4 rock layers, filter/underlayer
- residual cover after reshaping >= MTOC and >= DOC, the larger governs (Section 7.9 logic)
Falling apron (Eq. 27) stays out of the tool: it needs htot (edge scour depth), which has
no validated prediction for rock berms (Deltares Section 5.2.3.1). Keep it qualitative.

## 7. Output per KP
- the recommended method with the reason, and the others for comparison
- a set of candidate berms: each D50 with its geometry (slope, width, height), tonnage,
  for 2650 and 3000 kg/m3. The trade-off is decided together with the client.

## 8. Case studies (results/validation)
- three real NKT projects, all data supplied, project names not disclosed. Run the
  finished tool on them for the results and validation chapter.

## 9. Open questions
- damage-measure mapping (r vs Nod vs deformation class): no validated relation exists.
  Keep methods separate, use a fixed reference damage only for the comparison.
- RoBeD is offshore calibrated, used nearshore: state this honestly.
- angle-reduction rule from the roses: needs a defensible, documented rule.

## 10. Working style (apply everywhere)
- simple, well-commented code that any NKT colleague can use. Willem wants to understand
  every line, so build in small parts and explain.
- no em-dashes and no semicolons in thesis text or external messages.
- keep flagging real errors, do not drop them after one mention.
- verify formulas against the PDFs in papers/, and state confidence honestly.
- never edit the Word thesis directly. Give text to paste, or make separate files.

## 11. Repo / git note
- Pushing is currently blocked by a 403 organisation-policy on the git proxy, so commits
  may not persist across sessions. If push fails, deliver files to Willem directly so he
  can upload them. Earlier pushes in the session did work, so the block may be temporary.
