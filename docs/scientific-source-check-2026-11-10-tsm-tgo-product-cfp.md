# TSM Thai Sugar Ethanol: TGO-listed product CFP

**Reviewed:** 10 November 2026

**Status:** `HOLD_CONTEXT` pending the team's reuse-rights/profile check and certificate-scope review; not in the default reference export, not a normalized exchange, and not a team-calculated lifecycle result.

**Source class:** TGO product CFP registry, cross-checked against the manufacturer's TSM Group page.

## Registry value and identity check

The TGO registry lists **เอทานอล 99.5% (Fuel Grade)** from **บริษัท น้ำตาลไทยเอทานอล จำกัด (สำนักงานใหญ่)** under certificate `TGO CFP FY26-600-6241`. The displayed functional unit is **1 litre**, the boundary field is **B2B**, and the reported carbon-footprint volume is **638 g CO₂e**. The approval date is 18 March 2026 and expiry date is 17 March 2029. The registry gives the address as 1/104 Moo 8, Tha Mai, Tha Maka, Kanchanaburi.

The TSM Group ethanol-business page independently identifies Thai Sugar Ethanol Co., Ltd. as its ethanol plant, says the plant produces ethanol from molasses, and gives the same 1/104 Moo 8, Tha Mai, Tha Maka, Kanchanaburi address. This is a strong company/site match between the registry record and the TSM Group facility page. The direct conversion is:

`638 g CO₂e / 1 L = 0.638 kg CO₂e/L`

This conversion only changes units; it does not reconstruct the product assessment.

## What this does and does not establish

This is a newly verified, official TGO product CFP value for fuel-grade ethanol registered to the same legal company and plant address used in the TSM project. It is substantially more relevant than a generic Thai ethanol benchmark or an organization-level CFO total. It is a strong candidate for an internal **TGO-listed product CFP reference for TSM's ethanol**, with the certificate, date, unit and B2B label visible, once the team's reuse profile and the certificate's stage coverage are resolved.

The TGO detail page does not disclose the calculation/reporting period, feedstock mix for the certified product, allocation, process-level inventory, verification sheet, emission-factor set, applicable PCR identifier, or stage-by-stage boundary. An HTML link inspection found no certificate-specific verification-sheet attachment on this record page; the two PDF links present belong to general site news/energy-factor slides, not this ethanol certificate. This does not prove that the certificate documentation is unavailable through another channel. The CFP value must remain source-reported and certificate-specific. Because the page labels the boundary `B2B`, do not present it as a vehicle-use/tank-to-wheel result or as proof that distribution after sale, vehicle operation and end-of-life are included. Do not combine it with the 2009 UNFCCC wastewater-project data or divide/scale it using current installed capacity or unmatched annual production.

TGO's general CFP description defines product CFP across lifecycle stages and explains that B2B products can be raw materials/intermediates whose emissions information is passed to downstream manufacturers. TGO's PCR page states that a PCR must be followed for CFP assessment and, where Thailand has no PCR, the assessor/consultant must submit a draft product specification to TGO. The TSM registry entry does not show which PCR or product specification was used. A separate TGO record for a different 95% ethanol product (Union Solution AA) explicitly cites the PCR for cassava ethanol; that is evidence for that separate product only and cannot be assigned to TSM's molasses-based ethanol. The TGO PCR page inspected did not show a molasses-ethanol PCR in the rendered entries reviewed; this limited page inspection is not proof that none exists. Requesting the TSM certificate verification sheet, applicable PCR/product specification, and scope statement from TGO/the company is needed before making a stronger stage-coverage claim.

## Recommended database treatment

- Keep at `HOLD_CONTEXT` pending rights/profile and certificate-scope review; if later accepted, preserve the source CF (`638 g CO₂e` per `1 litre`) and its unit conversion (`0.638 kg CO₂e/L`) in separate fields.
- Preserve certificate ID, product purity/grade, manufacturer, site, functional unit, B2B boundary, approval date and expiry date.
- Link the source observation to the TSM company/site using the exact legal name and matching address; do not infer a reporting year.
- Do not insert the value as an elementary flow, a methane result, a cradle-to-grave result, a measured emission, or an input to the team's TSM scenario.
- Do not publish the underlying verification sheet or inventory without clearance. The registry metadata is publicly viewable, but permissions for underlying assessment materials were not reviewed.

## Sources and locators

- [TGO registry: เอทานอล 99.5% (Fuel Grade), TGO CFP FY26-600-6241](https://thaicarbonlabel.tgo.or.th/index.php?action=WkdWMFlXbHM&lang=TH&mod=Y0hKdlpIVmpkSE5mWVhCd2NtOTJZV3c9&param=TWprek9UUT0): product value, certificate, manufacturer, address, functional unit, boundary, approval/expiry dates.
- [TSM Group ethanol business page](https://tsmgroup.co.th/about-us/affiliated-company/ethanol-business/): legal company, molasses feedstock description, plant address and 200,000 L/day installed capacity. Capacity is not actual output and is not used in this CFP conversion.
- [TGO CFP description](https://thaicarbonlabel.tgo.or.th/index.php?lang=EN&mod=Y0hKdlpIVmpkSE5mYVhNPQ): general CFP lifecycle definition and explanation of B2B intermediates.
- [TGO Product Category Rules page](https://thaicarbonlabel.tgo.or.th/index.php?lang=EN&mod=Y0hKdlpIVmpkSE5mY25Wc1pYTT0): states that the applicable PCR must be followed and gives the route for a product category without an existing Thai PCR.
- [Separate TGO 95% ethanol record](https://thaicarbonlabel.tgo.or.th/index.php?action=WkdWMFlXbHM&lang=TH&mod=Y0hKdlpIVmpkSE5mWVhCd2NtOTJZV3c9&param=TXpRMU16UT0): Union Solution AA record cites the cassava-ethanol PCR; this is not TSM data.

The TGO registry page was fetched on 10 November 2026 (HTTP 200; 54,124 bytes; SHA-256 `c5d25c8d378d0cb49d567710a796bb7673e2907f5dbc5662fed9b081e833d789`). The TSM Group ethanol-business page was fetched on the same date (HTTP 200; 274,963 bytes; SHA-256 `dfa03486a53cbc999f0ce940cdab27bfc5e74ec5082b4bbda9a5a4d778ea30c0`). The TGO PCR catalog page was fetched on 10 November 2026 (HTTP 200; 48,226 bytes; SHA-256 `6b8d7efa19d94185a43c7e821b623c2101079d3ed50c288e6ae90d7476034234`). The separate Union Solution AA record was fetched on the same date (HTTP 200; 54,653 bytes; SHA-256 `6e6af762f95b33f2f4a7a10ffecfaccfc7fbb85edec4faede93b75f1a16e4d35`). Hashes identify captured HTML responses and do not establish permission to reuse registry metadata or any underlying assessment material. No certificate copy, verification sheet, or stage-level inventory was obtained.
