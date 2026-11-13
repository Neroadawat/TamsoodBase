// Run only in the isolated, disposable Neo4j lab with product_inventory.csv
// mounted at /var/lib/neo4j/import/product_inventory.csv.
CREATE CONSTRAINT exchange_observation_id IF NOT EXISTS
FOR (e:Exchange) REQUIRE e.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///product_inventory.csv' AS row
WITH row WHERE row.observation_id IS NOT NULL AND row.observation_id <> ''
MERGE (s:Entity:Source {id: 'source:' + row.source_snapshot_sha256})
  ON CREATE SET s.source_url = row.source_url,
                s.doi = row.doi,
                s.licence = row.licence,
                s.authors = row.authors
MERGE (p:Entity:Process {id: 'source:' + row.source_snapshot_sha256 + ':process:' + row.process})
  ON CREATE SET p.name = row.process,
                p.reference_amount = row.reference_amount,
                p.reference_unit = row.reference_unit,
                p.boundary = row.boundary,
                p.geography = row.geography,
                p.allocation = row.allocation,
                p.data_period = CASE WHEN row.data_period = '' THEN null ELSE row.data_period END,
                p.data_period_status = row.data_period_status
MERGE (e:Entity:Exchange {id: row.observation_id})
  SET e.observation_id = row.observation_id,
      e.flow_label = row.flow,
      e.direction = row.direction,
      e.role = row.role,
      e.subprocess = row.subprocess,
      e.raw_value = row.raw_value,
      e.amount = row.amount,
      e.unit = row.unit,
      e.publication_year = toInteger(row.publication_year),
      e.source_url = row.source_url,
      e.doi = row.doi,
      e.table_id = row.table_id,
      e.source_row = toInteger(row.source_row),
      e.source_column = toInteger(row.source_column),
      e.source_snapshot_sha256 = row.source_snapshot_sha256,
      e.licence = row.licence,
      e.authors = row.authors,
      e.boundary = row.boundary,
      e.geography = row.geography,
      e.technology_level = row.technology_level,
      e.allocation = row.allocation,
      e.annotation = CASE WHEN row.annotation = '' THEN null ELSE row.annotation END,
      e.status = row.status,
      e.is_national_average = toBoolean(row.is_national_average),
      e.is_full_lci_dataset = toBoolean(row.is_full_lci_dataset),
      e.is_newly_allocated = toBoolean(row.is_newly_allocated)
MERGE (f:Entity:Flow {id: 'source:' + row.source_snapshot_sha256 + ':flow:' + row.flow + '|' + row.unit})
  ON CREATE SET f.name = row.flow, f.identity_scope = 'SOURCE_LOCAL_LABEL_AND_UNIT'
MERGE (u:Entity:Unit {id: 'unit:' + row.unit})
  ON CREATE SET u.label = row.unit
MERGE (l:Entity:Location {id: 'location:' + row.geography})
  ON CREATE SET l.name = row.geography
MERGE (p)-[:HAS_EXCHANGE]->(e)
MERGE (e)-[:OF_FLOW]->(f)
MERGE (e)-[:IN_UNIT]->(u)
MERGE (e)-[:FROM_SOURCE]->(s)
MERGE (p)-[:FROM_SOURCE]->(s)
MERGE (p)-[:LOCATED_IN]->(l);
