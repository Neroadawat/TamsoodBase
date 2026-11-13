# TGO CFP for Thai Sugar Kanchanaburi molasses: upstream candidate

**Reviewed:** 10 November 2026  
**Status:** `HOLD_CONTEXT`; candidate upstream product-CFP reference only. Do not join to the TSM ethanol supply chain, calculate ethanol intensity, add to the team scenario, or release to public/RAG catalogs without source-identity, period, method, and rights review.

## What the source reports

The TGO product-CFP registry lists **กากน้ำตาล (โมลาส)** from **บริษัท น้ำตาลไทยกาญจนบุรี จำกัด (สำนักงานใหญ่)** under certificate `TGO CFP FY26-477-3693`. The record reports a functional unit of **1 tonne**, boundary **B2B**, and **92.3 kg CO₂e**. The approval date is 25 November 2025 and the expiry date is 24 November 2028. The listed address is 1 Moo 8, Saeng Chuto Road, Tha Mai, Tha Maka, Kanchanaburi 71120.

The unit-only conversion is `92.3 kg CO₂e / 1,000 kg molasses = 0.0923 kg CO₂e/kg molasses`. This remains the certified product CFP for that molasses product and boundary; it is not an elementary-flow inventory or a measured methane value.

## Relevance to the ethanol case, and the gap

TSM Group's sugar-business page names Thai Sugar Kanchanaburi Co., Ltd. and describes molasses among its sugar-production by-products. TSM Group's ethanol-business page says Thai Sugar Ethanol uses molasses as feedstock. These official pages establish that the producer and feedstock type are relevant to the same corporate group and product system.

They do **not** establish that the certified molasses in the TGO record was delivered to the ethanol plant, identify the supply period or quantity, or establish that its CFP method and scope can be used in the team's ethanol model. The registry record does not expose a reporting period, stage inventory, allocation method, applicable PCR/product specification, emission-factor set, or verification sheet. `B2B` does not by itself establish that transport to the ethanol plant or any later ethanol stages are covered.

A bounded review of every paginated title shown in TGO's PCR catalog covered 54 nationally listed and 266 general product rules. No listing title contained the literal Thai/English terms for ethanol, molasses, sugar, or biofuel. This is a catalog-title search only: it does not prove that no PCR applies, since a relevant rule may have another title, be available through a linked document, or be handled through a product specification. The TSM molasses certificate itself still does not disclose its applicable PCR.

TSM's ethanol-product page gives a qualitative process sequence: molasses is fermented with yeast under anaerobic conditions, the fermented ethanol is distilled to 95%, dehydrated to 99.5%, stored, and then sold to oil companies for gasohol production. This helps identify process steps for a future boundary map, but the page supplies no stage-level quantities, energy use, emissions, transport distances, or matched operating period. It also does not identify the certified molasses producer as the supplier for a specific period.

Therefore, this value may be useful as a separately identified, source-reported upstream candidate after review, but it cannot currently be used as the TSM ethanol plant's actual feedstock factor. Do not multiply it by a guessed molasses input ratio, join it to unmatched ethanol output, or add it to another product CFP that may cover overlapping stages.

## Recommended treatment

- Keep the record as `HOLD_CONTEXT`; record redistribution rights as `NOT_ASSESSED` and keep it out of default exports and RAG.
- Preserve the exact product, producer, certificate, FU, B2B boundary, dates, and source-reported value.
- Keep the 0.0923 kg CO₂e/kg unit conversion separate from the reported 92.3 kg CO₂e/t value.
- Require evidence of actual supplier/site relationship for the certified product, matched period and quantity, scope/PCR, and allocation before modeling this as an upstream input to ethanol.
- Keep missing period, feedstock delivery, stage allocation, and downstream transport values null. This record does not close the full-lifecycle ethanol gap.

## Sources

- [TGO registry: กากน้ำตาล (โมลาส), TGO CFP FY26-477-3693](https://thaicarbonlabel.tgo.or.th/index.php?action=WkdWMFlXbHM&lang=TH&mod=Y0hKdlpIVmpkSE5mWVhCd2NtOTJZV3c9&param=TWpjek9EST0): certificate, product, producer, address, FU, B2B boundary, CF value, approval and expiry dates.
- [TSM Group sugar business](https://tsmgroup.co.th/about-us/affiliated-company/sugar-business/): Thai Sugar Kanchanaburi identity, molasses as a by-product, and group-level resource circulation description.
- [TSM Group ethanol business](https://tsmgroup.co.th/about-us/affiliated-company/ethanol-business/): Thai Sugar Ethanol identity and molasses feedstock description.
- [TSM Group ethanol product/process page](https://tsmgroup.co.th/our-product/ethanol/): company-reported fermentation, distillation, dehydration, storage, and gasohol-distribution sequence; qualitative process disclosure only.
- [TGO Product Category Rules](https://thaicarbonlabel.tgo.or.th/index.php?lang=EN&mod=Y0hKdlpIVmpkSE5mY25Wc1pYTT0): CFP assessments must follow the applicable PCR; absence of a Thai PCR follows TGO's draft product-specification route.

The TGO registry HTML was fetched on 10 November 2026 (HTTP 200; 54,147 bytes; SHA-256 `da9121b748e995f5628d18132344276121f05194fca659718d3383f50a693a08`). The TSM sugar-business page was fetched on the same date (HTTP 200; 334,811 bytes; SHA-256 `7a7a666c8caba8c8637a48de06651ec8c384997927028073e09861b49f0fe318`). These hashes identify fetched HTML responses only; they do not grant reuse rights or establish supply-chain linkage.

The TSM ethanol-product page was fetched on the same date (HTTP 200; 528,272 bytes; SHA-256 `57d7682569d77d7a919177a541b40ecc84e44d2c10af0e4a589360091e7f483c`). Its process description is qualitative and does not close the quantitative LCI gaps.
