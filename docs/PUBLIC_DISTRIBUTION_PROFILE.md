# Public distribution contract v1

วันที่5พฤศจิกายน2569;โค้ดรุ่นใหม่ ยังไม่ใช่การรับรองสิทธิจากเจ้าของข้อมูล

Vercel proxy เป็นขอบเขต public ส่วน backend สำหรับงานวิจัยอยู่หลัง server-only upstream secret

- /api/model และ /api/release ส่งเฉพาะ B100 metadata/รุ่นโมเดลที่สร้างด้วย allowlist ไม่ส่ง330resultsหรือraw2019
- /api/reference และ /api/reference.json ใช้ field allowlist ส่งชื่อรายการ หน่วย ปี สถานะ และ source locator/link/hash ปริมาณ raw/scaled/payload/notes ที่อาจมีค่าซ้ำไม่ถูกส่งต่อ
- /api/reference.csv, /api/reports และ /api/report-pilot ปฏิเสธ403ในpublicproxyจนมีquantity distribution decision ไม่ถือคำเตือนNOT_CLEAREDเป็นใบอนุญาต
- upstream snapshot ปี2020ที่มี CC BY4.0 คงตามprojectionที่ตรวจเดิม ไม่เปลี่ยนสิทธิแหล่งอื่น
- การค้นสถิติDMF/NSO/EPPOยังใช้ชุดและนโยบายเดิม งานนี้ไม่อ้างว่าการตัดสินสิทธิทุกแหล่งสำเร็จ;ต้องทบทวนรายแหล่งก่อนขยายredistribution
- metadataที่เปิดต้องไม่มีcredentials/rawpayload/signedURL และไม่เปลี่ยน NOT_CLEARED เป็น CLEARED

การทดสอบเชิงลบอยู่ tests/vercel-proxy-behavior.cjs: แทรกปริมาณ/secretในnestedpayloadและmanifestแล้วต้องไม่ปรากฏในpublicprojection ทดสอบJSONmodelโดยไม่อาศัยupstreamcredentialsและCSVที่ยังไม่อนุญาตต้อง403 ไม่มีการเปิดrawPDF

หากต้องใช้ปริมาณcorporateในงานวิจัย ให้ใช้backendผ่านช่องทางทีมที่มีสิทธิเดิม ไม่ขยายpublicAPIหรือเปลี่ยนprofileเงียบ ๆ เมื่อตัดสินสิทธิในอนาคตต้องมีversionedallowlist/evidenceก่อนเปิดquantityfields
