# manpower has no ground-truth label in the data, so this is a transparent
# rule layer on top of the forecast, not a trained model. kept simple and
# explainable on purpose.

def recommend(forecast):
    sev = forecast["severity"]
    closure_p = forecast["closure_probability"]
    mins = forecast["expected_clearance_minutes"]

    officers = 1
    if sev == "High":
        officers += 1
    if mins > 60:
        officers += 1
    if closure_p >= 0.5:
        officers += 1

    barricade = closure_p >= 0.4

    if barricade:
        diversion = "Set up barricades and divert through-traffic to the parallel route."
    elif sev == "High":
        diversion = "Keep one lane clear and manage merging manually."
    else:
        diversion = "Monitor; clear the obstruction without diversion."

    rationale = (
        f"severity={sev}, closure_prob={closure_p:.0%}, "
        f"expected_clearance={mins:.0f}min"
    )

    return {
        "event_id": forecast["event_id"],
        "officers": officers,
        "barricade": barricade,
        "diversion_note": diversion,
        "rationale": rationale,
    }
