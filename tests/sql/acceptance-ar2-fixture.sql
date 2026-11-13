-- Small fixture for the AR-2 migration: one row of each kind the rule distinguishes.
USE tamsood_research;
INSERT INTO publisher VALUES ('DMF','กรมเชื้อเพลิงธรรมชาติ');
INSERT INTO product VALUES ('natural_gas','ก๊าซธรรมชาติ'),('crude_oil','น้ำมันดิบ');
INSERT INTO source_resource VALUES ('production-natural-gas','DMF','natural_gas','gas'),('production-oil','DMF','crude_oil','oil');
INSERT INTO resource_snapshot VALUES
 (REPEAT('a',64),'production-natural-gas','run','2026-10-22','https://example.invalid/gas.csv',REPEAT('1',64),REPEAT('2',64),'ลูกบาศก์ฟุต','ล้าน','Open Data Common','{}'),
 (REPEAT('b',64),'production-oil','run','2026-10-22','https://example.invalid/oil.csv',REPEAT('3',64),REPEAT('4',64),'บาร์เรล','','Open Data Common','{}');
INSERT INTO production_context VALUES
 (REPEAT('c',64),'production-natural-gas','ในทะเล',NULL,'เอราวัณ'),
 (REPEAT('d',64),'production-natural-gas','บนบก',NULL,'กำแพงแสน อู่ทอง สังฆจาย '),
 (REPEAT('e',64),'production-oil','บนบก',NULL,'สิริกิติ์ (LPG*, kgs.)'),
 (REPEAT('f',64),'production-oil','ในทะเล',NULL,'เบญจมาศ');
INSERT INTO source_record VALUES
 (REPEAT('a',64),2,'{}',REPEAT('0',64)),(REPEAT('a',64),3,'{}',REPEAT('0',64)),
 (REPEAT('b',64),2,'{}',REPEAT('0',64)),(REPEAT('b',64),3,'{}',REPEAT('0',64)),
 (REPEAT('b',64),4,'{}',REPEAT('0',64)),(REPEAT('b',64),5,'{}',REPEAT('0',64)),(REPEAT('b',64),6,'{}',REPEAT('0',64));
INSERT INTO observation (snapshot_id,source_line,context_id,period_start,raw_value,amount,production_days,identity_sha256) VALUES
 (REPEAT('a',64),2,REPEAT('c',64),'2024-03-01','207',207,31,REPEAT('5',64)),          -- accepted
 (REPEAT('a',64),3,REPEAT('d',64),'2020-02-01','3500000',3500000,29,REPEAT('6',64)),  -- magnitude hold
 (REPEAT('b',64),2,REPEAT('e',64),'2024-03-01','10',10,31,REPEAT('7',64)),            -- unit-label hold
 (REPEAT('b',64),3,REPEAT('f',64),'2024-03-01','100',100,31,REPEAT('8',64)),          -- accepted (representative)
 (REPEAT('b',64),4,REPEAT('f',64),'2024-03-01','100',100,31,REPEAT('8',64)),          -- exact copy
 (REPEAT('b',64),5,REPEAT('f',64),'2024-04-01','90',90,30,REPEAT('9',64)),            -- conflict
 (REPEAT('b',64),6,REPEAT('f',64),'2024-04-01','95',95,30,REPEAT('9',64));            -- conflict
INSERT INTO duplicate_disposition VALUES
 (REPEAT('a',64),2,'SINGLETON',NULL),(REPEAT('a',64),3,'SINGLETON',NULL),(REPEAT('b',64),2,'SINGLETON',NULL),
 (REPEAT('b',64),3,'EXACT_REPRESENTATIVE',NULL),(REPEAT('b',64),4,'EXCLUDE_EXACT_COPY',3),
 (REPEAT('b',64),5,'HOLD_CONFLICT',NULL),(REPEAT('b',64),6,'HOLD_CONFLICT',NULL);
