// Read-only query for the existing inventory lab graph.
// Supply $observation_id as a parameter from an approved inventory result.
MATCH (process:Process)-[:HAS_EXCHANGE]->(exchange:Exchange {observation_id: $observation_id})
RETURN process.name AS process, exchange.observation_id AS observation_id,
       exchange.direction AS direction, exchange.unit AS unit
LIMIT 10;
