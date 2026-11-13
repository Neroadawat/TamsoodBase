# Thai ethanol product CFP in the TGO registry

**Reviewed:** 10 November 2026

**Status:** `HOLD_CONTEXT` pending the team's reuse-rights/profile check and review of the certificate scope; not accepted into the default reference export, normalized LCI, or TSM scenario.

**Source class:** official TGO certificate-registry metadata.

## Verified registry entry

The Thailand Greenhouse Gas Management Organization (TGO) public registry lists **“Ethanol 99.5% 1 liters”**, certificate `TGO CFP FY26-727-7083`, manufactured by **P.S.C. STARCH PRODUCTS PUBLIC COMPANY LIMITED**. The entry reports a functional unit of **1 litre**, a boundary label of **B2B**, a carbon-footprint volume of **475 g CO₂e**, approval on **24 June 2026**, and expiry on **23 June 2029**. The registry also gives the manufacturer's address in Nong Yai District, Chonburi, Thailand. These fields are visible together on the TGO product record.

The direct unit conversion is:

`475 g CO₂e / 1 L = 0.475 kg CO₂e/L`

This is only a unit conversion of the displayed registry value. It is not a new emissions calculation.

## Interpretation and limits

This is a concrete Thai product-level CFP reference for ethanol and is stronger evidence than an organization-level CFO total for demonstrating a per-litre certified product metric. It can be shown as a **separate certified reference example**, with the manufacturer, product description, certificate number, functional unit, B2B label, and certificate validity shown beside the value.

It does not establish a representative factor for Thai ethanol generally, for TSM/Thai Sugar Ethanol, for a particular feedstock, or for the team's FAME/H-FAME system. Do not substitute `0.475 kg CO₂e/L` into the team's model or multiply it by project output without product, period, and boundary compatibility evidence.

TGO's general CFP description says product CFP concerns GHG emissions across product life-cycle stages, while also explaining that B2B products may be raw materials or intermediates whose GHG information is passed to downstream manufacturers. Therefore, the specific registry's **B2B** label must remain attached to this record. The registry detail page does not expose the underlying verification sheet, calculation period, allocation choices, emission-factor set, stage-by-stage inventory, transport/use/end-of-life coverage, or redistribution terms. We have not inspected a certificate PDF or underlying inventory and cannot claim that this entry alone proves a cradle-to-grave fuel result.

## Use in TamsoodBase

- Store/display as `ACCEPTED_REFERENCE` / source-reported product CFP metadata, not as a normalized LCI exchange.
- Keep the numeric source value and source unit (`475`, `g CO₂e`, per `1 litre`) alongside the converted display value (`0.475 kg CO₂e/L`).
- Keep the product identity and B2B boundary visible; do not label it “full lifecycle ethanol” without the underlying verification sheet confirming the included stages.
- Do not add the underlying inventory to public export, RAG, or the team's process model; the registry metadata does not grant redistribution rights to that inventory.
- A follow-up can request the verification sheet/PCR or technical scope from the manufacturer/TGO if the team needs stage coverage, reporting period, and allocation details. This is a human/source-access dependency, not a reason to guess.

## Sources

- TGO registry detail: [Ethanol 99.5% 1 liters, certificate TGO CFP FY26-727-7083](https://thaicarbonlabel.tgo.or.th/index.php?action=WkdWMFlXbHM&lang=EN&mod=Y0hKdlpIVmpkSE5mWVhCd2NtOTJZV3c9&param=TXpFMk1EYz0). Fields checked: product name, certificate, manufacturer, address, functional unit, boundary, CF volume, approval and expiry dates.
- TGO explanation: [Carbon Footprint of Product](https://thaicarbonlabel.tgo.or.th/index.php?lang=EN&mod=Y0hKdlpIVmpkSE5mYVhNPQ). Fields checked: CFP life-cycle description and explanation of B2B products as raw materials/intermediates supplied to downstream producers.

The registry HTML was fetched on 10 November 2026 (HTTP 200; 42,409 bytes; SHA-256 `81cd27a2d9daea065230d57be71eb6edf74617a031e261827fbb8dce5913de78`). The certificate document and underlying inventory were not reviewed. A page hash supports reproduction of this captured registry response but does not establish reuse rights.
