"""
Rock berm sizing tool for my MSc thesis (NKT / TU Delft).

What I want this tool to do: for a point along the cable route, find the smallest rock
size (Dn50) that stays stable for a free-standing rock berm over the cable. I do not want
to use one formula everywhere, so the tool first looks at the situation and then picks the
method that actually fits, and it shows the other methods next to it so I can compare.

The order I work in, per route point (KP):
    raw site data  ->  classify  ->  pick a method and check its validity  ->
    size it with every method that applies (for 2650 and 3000 kg/m3)  ->  compare

A few things I decided early on and want to keep visible:
  - I feed in the RAW measured numbers and let the code do the labelling. I do not want to
    decide myself beforehand whether a point is "steep" or "breaking".
  - I only choose the damage once, in the sizing. Each method keeps its own damage measure
    (Van Rijn r, Van der Meer Sd, Van Gent Nod) because I could not find a validated way to
    translate one into another. For the comparison I use one fixed reference per method.
  - I keep two slopes apart, because I mixed them up at first:
        seabed slope  -> comes from the survey, decides breaking / steep / Van Rijn validity
        berm slope cotalpha -> the side slope of the berm itself, that is a design choice,
                               and it goes into Hudson / Van der Meer / Van Gent.

Every formula below is written down from a paper and I put the reference next to it. Where a
number is a choice of mine and not from a paper, I say so (see group C).

Two things I fixed after checking the earlier NKT tool against the papers:
  - orbital velocity: the old code wrapped the sinh() argument in radians, but that argument
    is a plain ratio, not an angle. That gave velocities ~70x too high.
  - Van Rijn current friction has to be log base 10, not natural log. The paper writes
    fc = 0.24 / [log10(12h/ks)]^2. With natural log fc comes out ~5x too small, which would
    undersize the rock when the current dominates.
"""

import math

# ---------------------------------------------------------------------------
# GROUP A - physical constants. These are just physics, I do not touch them.
# ---------------------------------------------------------------------------
RHO_W = 1025.0            # sea water density [kg/m3]
G = 9.81                  # gravity [m/s2]
NU = 1.5e-6               # kinematic viscosity of water [m2/s]

RHO_ROCK_NORMAL = 2650.0  # normal rock [kg/m3]        (I compare both densities side by side)
RHO_ROCK_HIGH = 3000.0    # high-density rock [kg/m3]

# ---------------------------------------------------------------------------
# GROUP B - values I took straight from a paper. I can trace each one back, so I
# should not change them without changing the source I lean on.
# ---------------------------------------------------------------------------
BREAKING_INDEX = 0.5       # I call the significant wave "breaking" when Hs > 0.5*h.
                           # For Hs the depth limit is about 0.4-0.5 (Schiereck & Verhagen
                           # 2019, Sec 7.3.1). The 0.78-0.88 you often see is for a SINGLE
                           # wave, not for Hs, which is where the old code went wrong.
VDM_DEEP_RATIO = 3.0       # Van der Meer's deep-water form is fine while h/Hs >= 3 (my Ch5).
STEEP_SLOPE_RATIO = 0.10   # I call the seabed steep at 1:10, that is the slope Herrera &
                           # Medina used (m = 1/10).
DEFAULT_KD_NONBREAK = 4.0  # Hudson KD, rough angular rock, non-breaking (Rock Manual / SPM).
DEFAULT_KD_BREAK = 2.0     # Hudson KD, rough angular rock, breaking.
ALPHA_KS = 2.0             # bed roughness ks = 2*D50 (Van Rijn uses 1.5 to 2 times D50).

# ===========================================================================
# GROUP C - the numbers I still have to DECIDE with my supervisors.
# ---------------------------------------------------------------------------
# These are not from one paper, they are choices. For now I put in values that are
# reasonable so the tool runs and I can compare the methods, but the final numbers have
# to be agreed. I can also override every one of them per route point through the input,
# so none of this is locked into the calculation.
#
#   Decision 1 - the damage level per method (r, Sd, Nod)
#   Decision 2 - when I treat a current as "significant"
#   Decision 3 - the turbulence factor for a free-standing berm
#   Decision 4 - the standard berm geometry (slope, permeability, storm length, toe size)
# I also wrote these out in docs/PARAMETERS_TO_DECIDE.md.
# ===========================================================================

# Decision 1 - reference damage per method. These three are NOT the same thing, and I
# could not find a validated link between them. They set how much movement I accept, which
# drives the stone size.
REFERENCE_R_VANRIJN = 1.0    # Van Rijn r: 0.4 (strict) up to 1.0 (a lot of movement).
REFERENCE_SD_VDM = 2.0       # Van der Meer Sd: about 2 = start of damage, 8+ = failure.
REFERENCE_NOD_VANGENT = 0.5  # Van Gent Nod (displaced stones): about 0.5 low, 2+ high.

# Decision 2 - when is a current worth taking into account.
CURRENT_SIGNIFICANT = 0.2    # [m/s]. Above this I send the point to Van Rijn (wave+current).
                             # This threshold is my own guess, not from a paper.

# Decision 3 - turbulence factor in Van Rijn.
# Van Rijn 2019 gives gstr = 1 + n*gamma, with n = 2-3 and gamma = 0.2-0.3, so gstr sits
# between 1 and 2. gstr = 1.9 is the top end (n=3, gamma=0.3), gstr ~ 1.1 is near the bottom.
# Those END VALUES are from Van Rijn. What is NOT from Van Rijn is tying gstr to the blockage
# ratio (berm height / water depth) with the 5% and 25% thresholds below. That mapping is my
# own engineering judgement: a berm that blocks more of the water column squeezes the flow and
# raises the turbulence over the crest, so more blockage -> higher gstr. The thresholds are a
# modelling choice to document and agree, they are not measured.
DEFAULT_TURB_GSTR = 1.9      # the value in use for now. I think 1.9 is TOO HIGH for a
                             # free-standing cable berm (it fits high turbulence right next to
                             # a big structure) and it probably has to come down, but the right
                             # value is a decision for my supervisors, not an assumption of mine.
# Constants for the turbulence_factor PROPOSAL below (off by default, see that function).
GSTR_LOW = 1.1              # gstr at low blockage (near "no structure", Van Rijn lower end).
GSTR_HIGH = 1.9            # gstr at high blockage (Van Rijn upper end, n=3, gamma=0.3).
BLOCKAGE_LOW = 0.05        # blockage ratio at or below which I use GSTR_LOW (5%).
BLOCKAGE_HIGH = 0.25      # blockage ratio at or above which I use GSTR_HIGH (25%).

# Decision 4 - my standard berm geometry until I know better.
DEFAULT_COTALPHA = 2.0       # berm side slope 1:2 (Van Gent tested 1:1.5 and 1:2). Later I
                             # want to vary this to show the stone / slope / volume trade-off.
DEFAULT_P = 0.4              # permeability (0.1 = tight, 0.6 = fully rubble). 0.4 = open core.
DEFAULT_N_WAVES = 3000.0     # number of waves in the design storm (damage grows with sqrt(N)).
DEFAULT_BT = 3.0             # Van Gent berm width Bt [m], placeholder for now.
DEFAULT_TT = 1.0             # Van Gent berm thickness tt [m], placeholder for now.


# ---------------------------------------------------------------------------
# Small helper functions I use everywhere
# ---------------------------------------------------------------------------
def relative_density(rho_rock):
    """Relative buoyant density Delta = (rho_s - rho_w) / rho_w."""
    return (rho_rock - RHO_W) / RHO_W


def wavelength(period, h):
    """
    Local wavelength from linear wave theory. The dispersion relation is
        L = (g T^2 / 2pi) * tanh(2pi h / L)
    and L sits on both sides, so I cannot solve it directly. I start from the deep-water
    value and keep filling it back in until it stops changing. period [s], h [m] -> L [m].
    """
    L = G * period ** 2 / (2 * math.pi)     # first guess = deep-water wavelength
    for _ in range(100):
        L_new = (G * period ** 2 / (2 * math.pi)) * math.tanh(2 * math.pi * h / L)
        if abs(L_new - L) < 1e-6:           # L has settled, stop
            break
        L = L_new                           # otherwise take the new L and try again
    return L


def orbital_velocity(Hs, period, h, L):
    """
    Peak orbital velocity near the bed, linear wave theory:
        u_w = pi * Hs / (T * sinh(2pi h / L))
    Note to self: the sinh() argument is a ratio, not an angle. Wrapping it in radians was
    the big mistake in the old tool (velocities came out ~70x too high). [m/s].
    """
    return math.pi * Hs / (period * math.sinh(2 * math.pi * h / L))


# ---------------------------------------------------------------------------
# Step 1 - classification. Turn the raw survey / metocean numbers into labels.
# ---------------------------------------------------------------------------
def classify_seabed(soil_type):
    """My scope is only bedrock and mobile sand. Anything else I flag instead of using it."""
    s = soil_type.strip().lower()
    if s in ("rock", "bedrock", "hard"):
        return "bedrock"
    if s in ("sand", "mobile sand", "sandy"):
        return "mobile_sand"
    return "out_of_scope"


def seabed_is_steep(bed_slope_deg):
    """Steep if the seabed slope, written as a ratio, is 1:10 or steeper."""
    return math.tan(math.radians(bed_slope_deg)) >= STEEP_SLOPE_RATIO


def waves_are_breaking(Hs, h):
    """Depth-limited breaking of the significant wave: Hs above BREAKING_INDEX times depth."""
    return Hs > BREAKING_INDEX * h


def current_is_significant(uc):
    return uc > CURRENT_SIGNIFICANT


def van_der_meer_regime(h, Hs):
    """
    Which Van der Meer form I should use, based only on h and Hs (my Ch5):
      "deep"    -> h/Hs >= 3, the wave heights are still Rayleigh, normal deep-water form.
      "shallow" -> h/Hs < 3, the highest waves break off and I need the shallow-water form.
    """
    if Hs <= 0:
        return "unknown"
    return "deep" if (h / Hs) >= VDM_DEEP_RATIO else "shallow"


# ---------------------------------------------------------------------------
# Step 2 - pick the method (this is my decision tree for the smallest rock size).
# ---------------------------------------------------------------------------
def recommend_method(seabed, steep, breaking, current, regime="deep"):
    """
    Gives back (recommended_method, reason, comparisons).
      comparisons -> other methods I also want to run next to the main one, so I can put the
                     sizes side by side (that comparison is really the point of my thesis).
    I check the strongest thing first: a current, because Van Rijn is the only method that
    can do wave and current together.
    """
    if current:
        return "van_rijn", "current is significant, and Van Rijn is the only method for combined wave+current", []

    if seabed == "mobile_sand":
        return "van_rijn", "bed protection on a mobile sandy bed is what Van Rijn is made for", []

    if seabed == "bedrock":
        if steep and breaking:
            return "none", "steep bedrock with breaking waves: no rock-size method is valid, this needs Herrera & Medina (Nod branch)", []
        if breaking:
            return ("van_gent",
                    "waves break in shallow water on bedrock, Van Gent's h/Hs range fits the breaker zone",
                    [("van_der_meer_shallow", "the corrected Van der Meer is also valid in the breaker zone, so I run it to compare")])
        if regime == "shallow":
            return ("van_der_meer_shallow",
                    "not breaking but still shallow (h/Hs < 3): use the shallow-water Van der Meer",
                    [])
        return "van_der_meer", "wave-driven, not breaking, deep enough (h/Hs >= 3): standard Van der Meer fits", []

    return "none", "seabed type is out of my scope (only bedrock and mobile sand)", []


# ---------------------------------------------------------------------------
# Step 3 - validity checks I can do before running a formula.
# Each one gives back (is_valid, list_of_reasons). If a method is out of range I want to
# see WHY, I do not want a number I cannot trust.
# ---------------------------------------------------------------------------
def check_van_rijn(seabed, steep, current):
    reasons = []
    if steep:
        reasons.append("Van Rijn needs a horizontal or mild seabed slope")
    return (len(reasons) == 0), reasons


def check_van_der_meer(current, breaking, regime):
    """The standard deep-water Van der Meer."""
    reasons = []
    if current:
        reasons.append("Van der Meer is waves only (no current)")
    if breaking:
        reasons.append("the deep-water Van der Meer is not valid for breaking / depth-limited waves")
    if regime == "shallow":
        reasons.append("too shallow for the deep-water form (h/Hs < 3), use the shallow-water Van der Meer")
    return (len(reasons) == 0), reasons


def check_van_der_meer_shallow(current, regime):
    """The shallow-water Van der Meer (Van Gent 2004 coefficients)."""
    reasons = []
    if current:
        reasons.append("Van der Meer is waves only (no current)")
    if regime == "deep":
        reasons.append("deep enough (h/Hs >= 3), the correction is not needed, use the standard Van der Meer")
    return (len(reasons) == 0), reasons


def check_hudson(current):
    reasons = []
    if current:
        reasons.append("Hudson is waves only (no current)")
    return (len(reasons) == 0), reasons


def check_van_gent(current, h, Hs):
    reasons = []
    if current:
        reasons.append("Van Gent & Van der Werf is waves only (no current)")
    if Hs > 0:
        ratio = h / Hs
        if not (1.2 <= ratio <= 4.5):
            reasons.append(f"Van Gent needs h/Hs between 1.2 and 4.5 (here h/Hs = {ratio:.2f})")
    return (len(reasons) == 0), reasons


# ---------------------------------------------------------------------------
# Step 4 - the actual sizing formulas.
# Each one gives the required Dn50 [m] for a given rock density, at that method's reference
# damage. I wrote every formula out from its paper and put the reference in the docstring.
# ---------------------------------------------------------------------------

def hudson_dn50(Hs, rho_rock, cotalpha, KD):
    """
    Hudson (1958), the Dn50 form from the Rock Manual (CIRIA C683):
        Hs / (Delta * Dn50) = (KD * cotalpha)^(1/3)
    so Dn50 = Hs / ( Delta * (KD * cotalpha)^(1/3) ).
    KD is the stability coefficient (rough angular rock: about 4 non-breaking, 2 breaking).
    I only use Hudson as a rough first guess, never as my recommended answer.
    """
    Delta = relative_density(rho_rock)
    ns = (KD * cotalpha) ** (1.0 / 3.0)          # this is the stability number Hs/(Delta*Dn50)
    return Hs / (Delta * ns)


def _vandermeer_core(Hs, Tm, rho_rock, cotalpha, P, Sd, N, cpl, cs):
    """
    The shared Van der Meer (1988) machinery. Both the deep and the shallow form use exactly
    this, only the two fitted coefficients (cpl, cs) and the period differ. I kept it in one
    place so I do not copy the formula twice. Returns Dn50 [m].
    Reference: Van der Meer (1988), shallow coefficients from Van Gent (2004).
    """
    Delta = relative_density(rho_rock)
    tan_alpha = 1.0 / cotalpha
    sm = 2 * math.pi * Hs / (G * Tm ** 2)         # wave steepness with the mean period
    xi = tan_alpha / math.sqrt(sm)                # surf-similarity (Iribarren) number
    # which branch: plunging or surging
    xi_cr = (cpl / cs * P ** 0.31 * math.sqrt(tan_alpha)) ** (1.0 / (P + 0.5))
    if xi < xi_cr:
        ns = cpl * P ** 0.18 * (Sd / math.sqrt(N)) ** 0.2 * xi ** (-0.5)      # plunging
    else:
        ns = cs * P ** (-0.13) * (Sd / math.sqrt(N)) ** 0.2 * math.sqrt(cotalpha) * xi ** P  # surging
    return Hs / (Delta * ns)


def vandermeer_dn50(Hs, Tm, rho_rock, cotalpha=DEFAULT_COTALPHA, P=DEFAULT_P,
                    Sd=REFERENCE_SD_VDM, N=DEFAULT_N_WAVES):
    """Standard deep-water Van der Meer (1988): cpl = 6.2, cs = 1.0, mean period Tm."""
    return _vandermeer_core(Hs, Tm, rho_rock, cotalpha, P, Sd, N, cpl=6.2, cs=1.0)


def vandermeer_shallow_dn50(Hs, Tm_min10, rho_rock, cotalpha=DEFAULT_COTALPHA, P=DEFAULT_P,
                            Sd=REFERENCE_SD_VDM, N=DEFAULT_N_WAVES):
    """
    Shallow-water Van der Meer, the recalibrated form of Van Gent (2004): cpl = 8.4, cs = 1.3,
    and it uses the spectral period Tm-1,0 instead of the mean period. Valid 0.25 <= Hs0/h <= 1.5.
    This is the "modified" form from the shallow-water slides my professor gave me. The other
    one (rewritten with explicit H2%) needs the Battjes-Groenendijk table, I did not build that
    one in yet.
    """
    return _vandermeer_core(Hs, Tm_min10, rho_rock, cotalpha, P, Sd, N, cpl=8.4, cs=1.3)


def vangent_dn50(Hs, Tm_min10, h, rho_rock, Bt=DEFAULT_BT, tt=DEFAULT_TT, Nod=REFERENCE_NOD_VANGENT, ht=None):
    """
    Van Gent & Van der Werf (2014) toe/berm stability, from Coastal Engineering 2014, Eq. 1 and 3.

    Characteristic velocity near the bed (Eq. 1):
        u_hat = Hs / (Tm-1,0 * sinh(k * ht)),   k = 2pi / L
    Required rock size (Eq. 3):
        Dn50 = 0.32 * (Hs / Nod^(1/3)) * (Bt/Hs)^0.1 * (tt/Hs)^(1/3) * (u_hat / sqrt(g*Hs))

    ht is the water depth above the berm. If I do not give it, I use the full depth h (low berm).
    One thing to be aware of: the density does not appear in Van Gent's fit, so the Dn50 comes
    out the same for 2650 and 3000. That is just how the formula is, and I report it as it is.
    Bt and tt are geometry choices, their exponents are small so the size is not very sensitive.
    """
    if ht is None:
        ht = h
    L = wavelength(Tm_min10, ht)
    k = 2 * math.pi / L
    u_hat = Hs / (Tm_min10 * math.sinh(k * ht))
    return 0.32 * (Hs / Nod ** (1.0 / 3.0)) * (Bt / Hs) ** 0.1 * (tt / Hs) ** (1.0 / 3.0) * (u_hat / math.sqrt(G * Hs))


def turbulence_factor(berm_height, water_depth, next_to_large_structure=False):
    """
    PROPOSAL, not used by default. This is an idea I want to put to my supervisors, not a
    formula from a paper. It is off unless a point sets use_dynamic_gstr=True. By default the
    tool uses the fixed gstr (Decision 3), because I believe 1.9 is too high for a
    free-standing cable berm and the right value has to be agreed, not assumed.

    The idea: instead of one fixed turbulence factor gstr, compute it from the berm itself.
    Van Rijn 2019 gives gstr = 1 + n*gamma (n=2-3, gamma=0.2-0.3), so gstr is between 1 and 2.
    I use that range for the two ends (GSTR_LOW near "no structure", GSTR_HIGH at the top).
    How I move between them is my own choice: I use the blockage ratio of the berm, defined
    as berm height / water depth. A higher berm blocks more of the water column, squeezes the
    flow over the crest and raises the turbulence, so a higher blockage gives a higher gstr,
    and a deeper site with a smaller berm gives a lower one. The 5% and 25% thresholds are a
    modelling choice, not from a paper.

      blockage <= 5%   -> GSTR_LOW  (deep water / minor protrusion)
      blockage >= 25%  -> GSTR_HIGH (shallow water / high blockage)
      in between        -> linear interpolation
      next to a large structure (monopile, foundation) -> forced to GSTR_HIGH, because the
      vortices shed by the big structure dominate the turbulence.

    water_depth must be > 0 (defensive check).
    """
    if water_depth <= 0:
        raise ValueError("water_depth must be greater than 0 to compute the blockage ratio")
    if next_to_large_structure:
        return GSTR_HIGH                         # big-structure vortices dominate
    blockage = berm_height / water_depth
    if blockage <= BLOCKAGE_LOW:
        return GSTR_LOW
    if blockage >= BLOCKAGE_HIGH:
        return GSTR_HIGH
    # linear interpolation between the two ends
    frac = (blockage - BLOCKAGE_LOW) / (BLOCKAGE_HIGH - BLOCKAGE_LOW)
    return GSTR_LOW + frac * (GSTR_HIGH - GSTR_LOW)


def vanrijn_dn50(Hs, Tp, h, uc, rho_rock, r=REFERENCE_R_VANRIJN, gstr=DEFAULT_TURB_GSTR,
                 alpha_ks=ALPHA_KS, Ka1=1.0, Ka2=1.0, wave_current_angle_deg=0.0):
    """
    Van Rijn (2019), critical movement of large rocks in currents and waves. I solve for the
    smallest stable Dn50 under the combined wave-current bed shear. Because the roughness ks
    depends on D50 and D50 depends on the shear, I have to iterate.

    The steps (all from Van Rijn 2019):
      L      = wavelength from linear wave theory for Tp, h
      u_w    = pi*Hs/(Tp*sinh(2pi h/L))                     orbital velocity at the bed
      ks     = alpha_ks * D50   (1.5 to 2 * D50)            Nikuradse roughness
      A_w    = 0.5*Tp*u_w/pi                                orbital excursion
      f_c    = 0.24 / [log10(12h/ks)]^2                     current friction (log10, not ln)
      f_w    = exp(-6 + 5.2*(A_w/ks)^-0.19)                 wave friction
      tau_c  = 0.125*rho_w*f_c*(gstr*uc)^2                  current bed shear
      tau_w  = 0.25*f_w*rho_w*(gstr*u_w)^2                  wave bed shear
      tau_cw = combined shear (see the angle note below)
      D*     = D50*[(s-1)g/nu^2]^(1/3)                      dimensionless grain size
      th_cr  = 0.3/(1+D*) + 0.055*(1-exp(-0.02*D*))         critical Shields (Soulsby form)
      D50    = tau_cw / [(rho_s-rho_w)*g*Ka1*Ka2*r*th_cr]   the required size (Shields)
    r is the damage factor (1.0 = start of movement, lower = stricter, so a bigger stone).
    Ka1, Ka2 are the slope factors (both 1.0 on a flat bed). Returns Dn50 [m].

    Angle between waves and current (this is one of the main points of my thesis):
      Van Rijn Eq. 5 just adds tau_c + tau_w, which is the same as assuming the current and
      the waves point in the same direction (the worst case). If they are not aligned the
      combined shear is lower, so the stone can be smaller. I use the vector combination from
      Soulsby (1997) / DNV-RP-F109 (also Schiereck Sec 7.2):
          tau_cw = sqrt( (tau_c + tau_w*cos(phi))^2 + (tau_w*sin(phi))^2 )
      with phi the angle between the current and the wave direction. At phi = 0 this gives
      exactly tau_c + tau_w again, so the DEFAULT (phi = 0) stays on the safe side and matches
      Van Rijn. I only reduce the load once I give a real angle from the wave and current roses.
    """
    rho_s = rho_rock
    s = rho_s / RHO_W
    L = wavelength(Tp, h)
    u_w = orbital_velocity(Hs, Tp, h, L)
    A_w = 0.5 * Tp * u_w / math.pi
    phi = math.radians(wave_current_angle_deg)   # angle between current and waves

    # I iterate on D50 (fill it back in until it stops changing). For a case with big waves and
    # almost no current it can start jumping around, so I keep D50 inside a sensible band and
    # average old and new each step to calm it down. I also keep ks off zero so nothing blows up.
    D50 = 0.5          # first guess [m]
    for _ in range(500):
        ks = max(alpha_ks * D50, 1e-3)
        f_c = 0.24 / (math.log10(12 * h / ks)) ** 2
        f_w = math.exp(-6 + 5.2 * (A_w / ks) ** (-0.19))
        f_w = min(f_w, 0.3)                       # Van Rijn caps the wave friction in the rough regime
        tau_c = 0.125 * RHO_W * f_c * (gstr * uc) ** 2                 # current bed shear
        tau_w = 0.25 * f_w * RHO_W * (gstr * u_w) ** 2                 # wave bed shear
        # combined shear, angle-dependent (Soulsby / DNV-RP-F109). phi = 0 -> tau_c + tau_w.
        tau_cw = math.sqrt((tau_c + tau_w * math.cos(phi)) ** 2 + (tau_w * math.sin(phi)) ** 2)
        D_star = D50 * ((s - 1) * G / NU ** 2) ** (1.0 / 3.0)
        th_cr = 0.3 / (1 + D_star) + 0.055 * (1 - math.exp(-0.02 * D_star))
        D50_target = tau_cw / ((rho_s - RHO_W) * G * Ka1 * Ka2 * r * th_cr)
        D50_target = min(max(D50_target, 0.01), 5.0)    # keep it physical
        D50_new = 0.5 * (D50 + D50_target)              # average old and new to keep it stable
        if abs(D50_new - D50) < 1e-4:
            D50 = D50_new
            break
        D50 = D50_new
    return D50


# ---------------------------------------------------------------------------
# A validity check I can only do once I have the size (Van Rijn's grain-size range).
# ---------------------------------------------------------------------------
def van_rijn_size_valid(Dn50):
    """Van Rijn was validated for rock of 0.03 to 3 m (as sieve size D50, about 1.2 * Dn50)."""
    D50_sieve = 1.2 * Dn50
    if 0.03 <= D50_sieve <= 3.0:
        return True, []
    return False, [f"Van Rijn is validated for D50 0.03-3 m (here D50 is about {D50_sieve:.2f} m)"]


# ---------------------------------------------------------------------------
# Putting it together per route point: classify -> pick -> size with every method.
# ---------------------------------------------------------------------------
def _period_mean(Tp):
    """Mean period Tm, roughly Tp / 1.15 (rule of thumb for a JONSWAP-like spectrum)."""
    return Tp / 1.15


def _period_spectral(Tp):
    """Spectral period Tm-1,0, roughly Tp / 1.1 (rule of thumb for a single-peak spectrum)."""
    return Tp / 1.1


def size_with_method(method, point, rho_rock):
    """
    Run one method for one density. Gives back (Dn50 or None, short note). The 'point' dict
    holds the inputs, and if a method-specific input is missing I fall back to my defaults.
    """
    Hs, Tp, h = point["Hs"], point["Tp"], point["h"]
    Tm = _period_mean(Tp)
    Tm10 = _period_spectral(Tp)
    cotalpha = point.get("cotalpha", DEFAULT_COTALPHA)
    breaking = waves_are_breaking(Hs, h)

    if method == "van_rijn":
        phi = point.get("wave_current_angle", 0.0)   # degrees between waves and current, 0 = aligned (safe default)
        # Turbulence factor gstr. By default I use the FIXED value (a parameter to decide with
        # my supervisors, see Decision 3). The blockage-ratio model is only a PROPOSAL and is
        # off unless a point explicitly sets use_dynamic_gstr=True, because I could not find
        # that relationship in a paper.
        if point.get("use_dynamic_gstr", False):
            gstr = turbulence_factor(point.get("berm_height", 0.0), h,
                                     next_to_large_structure=point.get("next_to_large_structure", False))
        else:
            gstr = point.get("gstr", DEFAULT_TURB_GSTR)
        note = "combined wave+current shear" if phi == 0 else f"combined shear, waves/current angle {phi:.0f} deg"
        note += f"  [gstr={gstr:.2f}]"
        return vanrijn_dn50(Hs, Tp, h, point.get("uc", 0.0), rho_rock,
                            r=point.get("r", REFERENCE_R_VANRIJN),
                            gstr=gstr, wave_current_angle_deg=phi), note
    if method == "van_der_meer":
        return vandermeer_dn50(Hs, Tm, rho_rock, cotalpha, P=point.get("P", DEFAULT_P)), "deep-water form (cpl=6.2, cs=1.0)"
    if method == "van_der_meer_shallow":
        return vandermeer_shallow_dn50(Hs, Tm10, rho_rock, cotalpha, P=point.get("P", DEFAULT_P)), "shallow form, Van Gent 2004 (cpl=8.4, cs=1.3, Tm-1,0)"
    if method == "van_gent":
        return vangent_dn50(Hs, Tm10, h, rho_rock,
                            Bt=point.get("Bt", DEFAULT_BT), tt=point.get("tt", DEFAULT_TT),
                            ht=point.get("ht")), "toe/berm formula (density-independent)"
    if method == "hudson":
        KD = DEFAULT_KD_BREAK if breaking else DEFAULT_KD_NONBREAK
        return hudson_dn50(Hs, rho_rock, cotalpha, KD), f"rough first estimate (KD={KD})"
    return None, "no sizing formula for this method"


def assess_point(point):
    """
    Full run for one KP: classify it, pick the method, and size it with every method that
    applies, for both rock densities.
    A point needs at least: soil_type, bed_slope_deg, h, Hs, Tp, uc.
    Optional design inputs: cotalpha, P, r, Bt, tt, ht.
    """
    seabed = classify_seabed(point["soil_type"])
    if seabed == "out_of_scope":
        return {"id": point.get("id"), "seabed": seabed,
                "note": "seabed type out of scope (only bedrock / mobile sand)"}

    steep = seabed_is_steep(point["bed_slope_deg"])
    breaking = waves_are_breaking(point["Hs"], point["h"])
    current = current_is_significant(point["uc"])
    regime = van_der_meer_regime(point["h"], point["Hs"])

    recommended, reason, comparisons = recommend_method(seabed, steep, breaking, current, regime)

    validity = {
        "van_rijn": check_van_rijn(seabed, steep, current),
        "van_der_meer": check_van_der_meer(current, breaking, regime),
        "van_der_meer_shallow": check_van_der_meer_shallow(current, regime),
        "hudson": check_hudson(current),
        "van_gent": check_van_gent(current, point["h"], point["Hs"]),
    }

    # I only size the method(s) I am ALLOWED to use here: the recommended one and any method I
    # explicitly want to compare it with. Every other method is left without a number and shown
    # as "not valid for this situation" in the report, so I never present a size from a formula
    # that does not apply to this point.
    sizing = {}
    methods_to_size = set([recommended] + [m for m, _ in comparisons])
    methods_to_size.discard("none")
    for m in sorted(methods_to_size):
        row = {}
        for label, rho in (("normal_2650", RHO_ROCK_NORMAL), ("high_3000", RHO_ROCK_HIGH)):
            dn50, note = size_with_method(m, point, rho)
            # the size-dependent Van Rijn check goes here, once I have the number
            size_flag = ""
            if m == "van_rijn" and dn50 is not None:
                ok, why = van_rijn_size_valid(dn50)
                if not ok:
                    size_flag = "  [" + "; ".join(why) + "]"
            row[label] = (dn50, note + size_flag)
        sizing[m] = row

    return {
        "id": point.get("id"),
        "seabed": seabed, "steep": steep, "breaking": breaking,
        "current_significant": current, "vdm_regime": regime,
        "recommended": recommended, "reason": reason, "comparisons": comparisons,
        "validity": validity, "sizing": sizing,
    }


# ---------------------------------------------------------------------------
# Printing to the terminal
# ---------------------------------------------------------------------------
def print_decisions():
    """
    Print the numbers I still have to decide (group C). These are placeholders until I agree
    them with my supervisors, and I can override each one per point. I print them at the top
    of every run so I never forget they are not final.
    """
    print("#" * 74)
    print("# PARAMETERS TO DECIDE (placeholders until agreed with my supervisors)")
    print("#" * 74)
    print(f"  Decision 1  damage per method (this drives the stone size):")
    print(f"      Van Rijn   r   = {REFERENCE_R_VANRIJN}   (0.4 strict .. 1.0 much movement)")
    print(f"      Van der Meer Sd = {REFERENCE_SD_VDM}   (2 start of damage .. 8+ failure)")
    print(f"      Van Gent   Nod = {REFERENCE_NOD_VANGENT}   (0.5 low .. 2+ high damage)")
    print(f"  Decision 2  current is 'significant' above  {CURRENT_SIGNIFICANT} m/s")
    print(f"  Decision 3  turbulence factor gstr = {DEFAULT_TURB_GSTR}  (I think this is too high for a")
    print(f"              free-standing berm and it should come down. A blockage-based model is")
    print(f"              coded as a PROPOSAL (turbulence_factor), off by default.)")
    print(f"  Decision 4  geometry defaults: cot(alpha)={DEFAULT_COTALPHA}, P={DEFAULT_P}, "
          f"N={int(DEFAULT_N_WAVES)}, Bt={DEFAULT_BT} m, tt={DEFAULT_TT} m")
    print("#" * 74)
    print()


def print_report(r):
    print("=" * 74)
    print(f"POINT: {r['id']}")
    if r["seabed"] == "out_of_scope":
        print(f"  -> {r['note']}")
        return
    print(f"  seabed={r['seabed']}  steep={r['steep']}  breaking={r['breaking']}  "
          f"current={r['current_significant']}  vdm_regime={r['vdm_regime']}")
    print(f"  RECOMMENDED: {r['recommended']}  ({r['reason']})")
    for method, note in r["comparisons"]:
        print(f"  ALSO RUN:    {method}  ({note})")

    print(f"  {'-'*70}")
    print(f"  Required Dn50 [m]      2650 kg/m3   3000 kg/m3   notes")
    # I list every method, but only the ones I may use here get a size. The rest are shown as
    # not valid, with the reason, so it is clear I did not just skip them.
    all_methods = ["van_rijn", "van_der_meer", "van_der_meer_shallow", "van_gent", "hudson"]
    for method in all_methods:
        if method in r["sizing"]:
            row = r["sizing"][method]
            d_n = row["normal_2650"][0]
            d_h = row["high_3000"][0]
            note = row["normal_2650"][1]
            star = " *" if method == r["recommended"] else "  "
            dn_s = f"{d_n:8.3f}" if d_n is not None else "   n/a  "
            dh_s = f"{d_h:8.3f}" if d_h is not None else "   n/a  "
            print(f"  {star}{method:22s}{dn_s}     {dh_s}     {note}")
        else:
            # not a method I may use here: say why instead of giving a number
            ok, reasons = r["validity"].get(method, (False, []))
            if reasons:
                why = "not valid here: " + "; ".join(reasons)
            else:
                why = "not the method selected for this situation"
            print(f"    {method:22s}{'not valid':>8}     {'-':>8}     {why}")
    print(f"  (* = recommended method. A size is only shown for the method(s) that apply here.")
    print(f"     Where two methods are shown, their damage measures differ, so read as a comparison.)")


# ---------------------------------------------------------------------------
# Quick self-test so I can see the routing and the sizes on a few example points.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo_points = [
        {"id": "sand, mild, strong current", "soil_type": "sand", "bed_slope_deg": 0.3,
         "h": 18.1, "Hs": 4.98, "Tp": 11.0, "uc": 1.68},
        # These two show the gstr PROPOSAL (opt-in with use_dynamic_gstr), not the default.
        {"id": "sand, current, low berm (gstr proposal, opt-in)", "soil_type": "sand", "bed_slope_deg": 0.3,
         "h": 18.1, "Hs": 4.98, "Tp": 11.0, "uc": 1.68, "berm_height": 1.5, "use_dynamic_gstr": True},
        {"id": "sand, current, next to monopile (gstr proposal, opt-in)", "soil_type": "sand", "bed_slope_deg": 0.3,
         "h": 18.1, "Hs": 4.98, "Tp": 11.0, "uc": 1.68, "berm_height": 1.5,
         "use_dynamic_gstr": True, "next_to_large_structure": True},
        {"id": "bedrock, non-breaking, deep", "soil_type": "bedrock", "bed_slope_deg": 1.0,
         "h": 25.0, "Hs": 6.85, "Tp": 12.0, "uc": 0.1},
        {"id": "bedrock, non-breaking, shallow (transition)", "soil_type": "bedrock", "bed_slope_deg": 1.0,
         "h": 18.0, "Hs": 7.0, "Tp": 12.0, "uc": 0.1},
        {"id": "bedrock, breaking", "soil_type": "bedrock", "bed_slope_deg": 2.0,
         "h": 8.0, "Hs": 5.0, "Tp": 10.0, "uc": 0.1},
        {"id": "bedrock, steep + breaking", "soil_type": "bedrock", "bed_slope_deg": 7.0,
         "h": 5.0, "Hs": 4.8, "Tp": 9.0, "uc": 0.1},
        {"id": "clay (out of scope)", "soil_type": "Clay", "bed_slope_deg": 0.8,
         "h": 24.6, "Hs": 6.33, "Tp": 11.0, "uc": 0.38},
    ]
    print_decisions()
    for p in demo_points:
        print_report(assess_point(p))
