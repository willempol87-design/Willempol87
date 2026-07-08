"""
Nearshore rock-berm sizing tool  (thesis version, built from scratch)
=====================================================================

Goal of the tool: given the site conditions of a point along the cable route,
work out the smallest feasible rock size (Dn50) for a free-standing rock berm,
using the RIGHT method for that situation and showing the others for comparison.

This file is built up in parts so every line stays readable:
  PART 1 (this file so far): read the raw site data, classify it, pick the
          method with a decision tree, and check each method's validity range.
  PART 2 (next): the actual sizing formulas (Hudson, Van der Meer, Van Rijn,
          Van Gent & Van der Werf), each run for 2650 and 3000 kg/m3 rock.

Design choices already agreed:
  - Output-first: the user first says WHAT they want (here: minimal rock size).
  - We keep the RAW measured numbers as input and let the code classify them.
    The user never has to pre-label things as "steep" or "breaking".
  - Scope: nearshore, from the shoaling zone up to just past the breaker line.
    NOT the very-shallow inner surf. So the Van der Meer shallow-water form is
    not part of this tool.

Two different slopes (kept apart on purpose, this was wrong in the old code):
  - seabed slope  : from the survey. Drives breaking, steep/mild, Van Rijn validity.
  - berm slope cotα : the side slope of the rock berm itself. A DESIGN choice,
                      used inside Hudson / Van der Meer / Van Gent. Comes later.
"""

import math

# ----------------------------------------------------------------------------
# Adjustable constants. These are the only "knobs". Change them here, in one
# place, and everything downstream follows. Every value is explained.
# ----------------------------------------------------------------------------
RHO_W = 1025.0            # sea water density [kg/m3]
G = 9.81                  # gravitational acceleration [m/s2]

RHO_ROCK_NORMAL = 2650.0  # normal rock density [kg/m3]  (design variable)
RHO_ROCK_HIGH = 3000.0    # high-density rock [kg/m3]     (design variable)

# Classification thresholds (raw number in, category out).
CURRENT_SIGNIFICANT = 0.2  # current speed above this [m/s] counts as "significant".
                           # Above it, only Van Rijn applies (the others are waves-only).
BREAKING_INDEX = 0.88      # waves are treated as breaking when Hs > BREAKING_INDEX * h.
                           # 0.88 is the breaker index used in the thesis (Schiereck & Verhagen).
STEEP_SLOPE_RATIO = 0.10   # seabed steeper than 1:10 counts as "steep" (Herrera & Medina m = 1/10).


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def relative_density(rho_rock):
    """Relative buoyant density  Delta = (rho_s - rho_w) / rho_w  [-]."""
    return (rho_rock - RHO_W) / RHO_W


# ----------------------------------------------------------------------------
# Classification: turn raw survey/metocean numbers into categories.
# ----------------------------------------------------------------------------
def classify_seabed(soil_type):
    """
    Only two seabed types are in scope (thesis Chapter 2): bedrock and mobile sand.
    Anything else (clay, etc.) is out of scope and is flagged, not silently accepted.
    """
    s = soil_type.strip().lower()
    if s in ("rock", "bedrock", "hard"):
        return "bedrock"
    if s in ("sand", "mobile sand", "sandy"):
        return "mobile_sand"
    return "out_of_scope"


def seabed_is_steep(bed_slope_deg):
    """Steep if the seabed slope (converted from degrees to a ratio) >= 1:10."""
    slope_ratio = math.tan(math.radians(bed_slope_deg))
    return slope_ratio >= STEEP_SLOPE_RATIO


def waves_are_breaking(Hs, h):
    """Depth-limited breaking when the wave height exceeds the breaker index times depth."""
    return Hs > BREAKING_INDEX * h


def current_is_significant(uc):
    return uc > CURRENT_SIGNIFICANT


# ----------------------------------------------------------------------------
# Method selection (decision tree) for the "minimal rock size" goal.
# Candidate methods: Hudson, Van der Meer, Van Rijn, Van Gent & Van der Werf.
# Hudson is never the recommended one, only ever a rough first-estimate check.
# ----------------------------------------------------------------------------
def recommend_method(seabed, steep, breaking, current):
    """
    Returns (recommended_method, reason). Strongest discriminator first:
    current, because Van Rijn is the only method that handles combined wave+current.
    """
    if current:
        return "van_rijn", "current is significant, and Van Rijn is the only method for combined wave+current"

    if seabed == "mobile_sand":
        return "van_rijn", "bed protection on a mobile sandy bed is Van Rijn's home ground"

    if seabed == "bedrock":
        if steep and breaking:
            # This corner is Herrera & Medina territory (a Nod method, other branch).
            # None of the four rock-size methods are valid here.
            return "none", "steep bedrock with breaking waves: no rock-size method is valid, this needs Herrera & Medina (Nod branch)"
        if breaking:
            return "van_gent", "waves break in shallow water on bedrock, Van Gent's h/Hs range fits the breaker zone"
        return "van_der_meer", "wave-dominated, non-breaking bedrock slope suits Van der Meer"

    return "none", "seabed type is out of scope (only bedrock and mobile sand are supported)"


# ----------------------------------------------------------------------------
# Validity gates. Each returns (is_valid, list_of_reasons_if_not).
# These encode the verified table (CIRIA C683, Van Rijn 2019, Van Gent 2014).
# Only the checks we can do BEFORE running a formula are here. The size-dependent
# gate (e.g. Van Rijn D50 = 0.03-3 m) is applied together with the formula in Part 2.
# ----------------------------------------------------------------------------
def check_van_rijn(seabed, steep, current):
    reasons = []
    if steep:
        reasons.append("Van Rijn needs a horizontal or mild seabed slope")
    # Van Rijn is fine with or without current, on sand or bedrock.
    return (len(reasons) == 0), reasons


def check_van_der_meer(current, breaking):
    reasons = []
    if current:
        reasons.append("Van der Meer is waves-only (no current)")
    if breaking:
        reasons.append("Van der Meer (deep-water form) is not valid for breaking/depth-limited waves")
    return (len(reasons) == 0), reasons


def check_hudson(current):
    reasons = []
    if current:
        reasons.append("Hudson is waves-only (no current)")
    return (len(reasons) == 0), reasons


def check_van_gent(current, h, Hs):
    reasons = []
    if current:
        reasons.append("Van Gent & Van der Werf is waves-only (no current)")
    if Hs > 0:
        ratio = h / Hs
        if not (1.2 <= ratio <= 4.5):
            reasons.append(f"Van Gent needs h/Hs between 1.2 and 4.5 (here h/Hs = {ratio:.2f})")
    return (len(reasons) == 0), reasons


# ----------------------------------------------------------------------------
# Process one point: classify -> recommend -> report validity of all methods.
# (No sizing yet, that is Part 2.)
# ----------------------------------------------------------------------------
def assess_point(point):
    """
    'point' is a dict with the raw inputs needed for classification:
       soil_type, bed_slope_deg, h, Hs, uc
    Returns a small result dict describing the classification and method choice.
    """
    seabed = classify_seabed(point["soil_type"])
    if seabed == "out_of_scope":
        return {"id": point.get("id"), "seabed": seabed,
                "note": "seabed type out of scope (only bedrock / mobile sand)"}

    steep = seabed_is_steep(point["bed_slope_deg"])
    breaking = waves_are_breaking(point["Hs"], point["h"])
    current = current_is_significant(point["uc"])

    recommended, reason = recommend_method(seabed, steep, breaking, current)

    # Which methods pass their pre-formula validity gate for this situation?
    validity = {
        "van_rijn": check_van_rijn(seabed, steep, current),
        "van_der_meer": check_van_der_meer(current, breaking),
        "hudson": check_hudson(current),
        "van_gent": check_van_gent(current, point["h"], point["Hs"]),
    }

    return {
        "id": point.get("id"),
        "seabed": seabed,
        "steep": steep,
        "breaking": breaking,
        "current_significant": current,
        "recommended": recommended,
        "reason": reason,
        "validity": validity,
    }


# ----------------------------------------------------------------------------
# Quick self-test on a few representative points (so we can see the routing work
# before any formulas exist). This block runs only when the file is run directly.
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    demo_points = [
        {"id": "sand, mild, current", "soil_type": "sand", "bed_slope_deg": 0.3, "h": 18.1, "Hs": 4.98, "uc": 1.68},
        {"id": "bedrock, non-breaking", "soil_type": "bedrock", "bed_slope_deg": 1.0, "h": 25.0, "Hs": 6.85, "uc": 0.1},
        {"id": "bedrock, breaking", "soil_type": "bedrock", "bed_slope_deg": 2.0, "h": 6.0, "Hs": 5.6, "uc": 0.1},
        {"id": "bedrock, steep + breaking", "soil_type": "bedrock", "bed_slope_deg": 7.0, "h": 5.0, "Hs": 4.8, "uc": 0.1},
        {"id": "clay (out of scope)", "soil_type": "Clay", "bed_slope_deg": 0.8, "h": 24.6, "Hs": 6.33, "uc": 0.38},
    ]

    for p in demo_points:
        r = assess_point(p)
        print("=" * 70)
        print(f"POINT: {r['id']}")
        if r["seabed"] == "out_of_scope":
            print(f"  -> {r['note']}")
            continue
        print(f"  seabed={r['seabed']}  steep={r['steep']}  breaking={r['breaking']}  current={r['current_significant']}")
        print(f"  RECOMMENDED: {r['recommended']}  ({r['reason']})")
        for method, (ok, reasons) in r["validity"].items():
            mark = "valid" if ok else "NOT valid"
            extra = "" if ok else "  <- " + "; ".join(reasons)
            print(f"     {method:15s}: {mark}{extra}")
