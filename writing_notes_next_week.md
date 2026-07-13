# Writing notes for next week (verified against sources)

Everything below was checked against the primary sources during this session. The
main reference the professor wants us to lean on is Schiereck and Verhagen (2019),
Introduction to Bed, Bank and Shore Protection (already in papers/). He helped write
that book, so it is the go-to for the physical reasoning.

## Meeting outcomes (prof. Antonini)
- Approval on the step plan and the figures. Keep everything sharp and defensible.
- Agreed that the damage level can be chosen already at the rock-size step (stage 1).
- Three case studies with the final code on three real NKT projects. NKT will not
  disclose which projects, but supplies all the data. This is the results/validation base.
- The wave-current angle as an optimisation was called a creative idea, with the caveat
  that conservative assumptions are often taken. So the angle reduction must be
  defensible, with a clear rule for when a reduction is allowed.

## Check 1 - combined wave and current on the bed (two flows). VERIFIED, strong.
Schiereck and Verhagen (2019), Section 7.2 "Waves and currents / Combined
wave-current action", Eq. 7.5 to 7.7, Figure 7-8, after Bijker (1967).
- Wave and current shear velocities are added vectorially. Resulting shear tau = rho*u*^2.
- There is a cross term with sin(phi), phi = angle between wave and current.
- KEY: for sediment transport (averaged over a wave cycle) the cross term vanishes and
  the shear is independent of the angle. But for BOTTOM PROTECTION the MAXIMUM shear
  governs, and that maximum IS angle dependent (max when wave and current are parallel).
- Example (Fig 7-8): current alone 4 N/m2, wave alone 47 N/m2, parallel 78.6 N/m2,
  perpendicular 51.4 N/m2. So alignment adds ~50%.
- CONSEQUENCE: the angle optimisation is textbook-grounded for our object (bottom
  protection). Worst case = parallel. Using the real angle justifies a smaller stone.

## Check 2 - breaking criterion. LIKELY WRONG in the tool, needs a fix.
Schiereck and Verhagen (2019), Section 7.3.1, Eq. 7.8, p.156.
- 0.88 (and 0.78 solitary) is the limit for an INDIVIDUAL wave H, not for Hs.
- Applied to the significant wave height, the depth-limited ratio is Hs/h ~ 0.4 to 0.5
  (because the largest waves, 1.5 to 2 Hs, break first).
- The tool uses is_breaking = Hs > 0.88*h, which under-detects breaking and can route
  to the wrong method. ACTION: change BREAKING_INDEX in nearshore_rock_tool.py to
  about 0.5 for Hs, and confirm the exact value with the professor.

## Check 3 - slope-based vs shear-stress-based methods. CONFIRMED.
- Shear stress / Shields (bed protection): Van Rijn, Deltares. Schiereck Ch. 3 (Shields).
- Stability number / slope (armour): Hudson, Van der Meer, Van Gent, Herrera.
  Schiereck Ch. 8. This difference in physical basis is why the methods do not compare
  cleanly. The structure of Schiereck itself supports this split.

## Check 4 - scour type: clear-water vs live-bed. VERIFIED, apply the distinction.
Schiereck and Verhagen (2019), Chapter 4 "Flow-Erosion", Figure 4-1, p.80-82.
- Clear-water: no sediment supply from upstream (S1 = 0). Stops when the velocity drops
  below critical. Slow, asymptotic, max slightly deeper.
- Live-bed: upstream flow already moves the bed (S1 > 0). Reaches equilibrium faster.
- Determinant is ambient velocity vs critical (u vs uc). Seabed type is a strong proxy.
- Our mapping: bedrock -> clear-water (no erodible material upstream). Sand -> live-bed
  (nearshore waves usually mobilise the sand). State it as "most likely", not "always".
- Bonus: Deltares handbook says the berm deformation resembles clear-water scour (the
  handbook text around the reshaping section), which links berm reshaping to clear-water.

## Check 5 - equilibrium scour and scour WITH protection. Concepts yes, formulas no.
Schiereck and Verhagen (2019), Section 4.3.5 and chapter summary, p.96 to 103,
Eq. 4.13 with the coefficient alpha (turbulence magnifying factor).
- APPLY the concepts and the design principle: scour cannot be prevented, its threat to
  the structure is the problem, keep the scour hole away from the cable (wider berm,
  gentler side slopes). With protection, scour reaches equilibrium more slowly.
- DO NOT use the specific formulas (Eq. 4.9 to 4.13) as a validated nearshore-berm scour
  depth. They are derived for jets, culverts, piers and outflow structures in
  current-dominated flow, Schiereck himself calls their physical basis meagre, and
  Deltares states there is no validated edge-scour method for rock berms. Keep htot
  qualitative, consistent with our earlier decision.

## Code finding to reuse as an example of method-mixing
The colleague tool sizes the stone with Van Rijn (damage via r) but then filters the
berm geometry with a toe-berm damage number Nod (the Muttray 2013 form
(0.58 - 0.17*..)^3 * Ns^3), and asks the user for a Maximum Nod. So it mixes two methods
with two damage measures in one calculation. This is a real-world example of exactly the
problem this thesis addresses. Do not use it as a basis.

## To write next week
1. Ch3/Ch7: the two-flows combined shear and the angle, using Schiereck Sec 7.2.
2. Fix the breaking criterion in the tool and describe it (Schiereck Sec 7.3.1).
3. Ch5/Ch7: sharpen the slope vs shear-stress distinction.
4. Ch6: add the clear-water vs live-bed distinction (bedrock vs sand) with the u vs uc
   nuance, and the scour-with-protection design principle from Schiereck p.96-103.
