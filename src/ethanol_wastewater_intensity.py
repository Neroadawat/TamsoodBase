"""Calculate a measured wastewater methane contribution on a matched output basis."""
from datetime import date
from decimal import localcontext

from src.carbon_calculator import characterize, provenance
from src.thai_carbon import quantity


def wastewater_intensity(production, emissions, factors, *, gas_id):
    """Accept net emitted methane and ethanol output for the same site and period."""
    for observation in (production, emissions):
        provenance(observation)
    keys = ("facility_id", "period_start", "period_end")
    if any(not production.get(key) or production[key] != emissions.get(key) for key in keys):
        raise ValueError("Both observations must identify the same facility and period")
    if date.fromisoformat(production["period_end"]) < date.fromisoformat(production["period_start"]):
        raise ValueError("Invalid monitoring period")
    if production.get("flow") != "fuel_ethanol_output" or production.get("unit") != "L":
        raise ValueError("Expected fuel ethanol output in litres")
    if emissions.get("flow") != "wastewater_methane_emitted" or emissions.get("gas_id") != gas_id:
        raise ValueError("Expected net emitted methane with matching gas identity")
    if gas_id not in {"CH4", "CH4_biogenic", "CH4_non_fossil", "CH4_fossil"}:
        raise ValueError("Expected a methane gas identity")
    if emissions.get("measurement_status") != "MEASURED":
        raise ValueError("Expected measured methane emissions")
    output = quantity(production["amount"])
    if output == 0:
        raise ValueError("Positive ethanol production required")
    basis = "/".join(production[key] for key in keys)
    result = characterize(
        emissions["amount"], emissions["unit"], gas_id, factors,
        basis_id=basis, coverage_id="wastewater_net_methane", source=emissions,
    )
    with localcontext() as ctx:
        ctx.prec = 60
        intensity = quantity(result["amount_kgCO2e"]) / output
    return {
        "scope": "WASTEWATER_METHANE_COMPONENT",
        "ethanol_output": dict(production),
        "characterized_methane": result,
        "kgCO2e_per_L_ethanol": format(intensity, "f"),
        "CO2e_total": None,
    }
