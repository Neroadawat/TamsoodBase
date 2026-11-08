"""Indexes for the Explorer's existing filters and deterministic ordering."""
INDEX_SQL = (
    'CREATE INDEX IF NOT EXISTS ix_candidate_recent ON candidate(year_ce DESC,month DESC,package,source_line)',
    'CREATE INDEX IF NOT EXISTS ix_candidate_package_recent ON candidate(package,year_ce DESC,month DESC,source_line)',
    'CREATE INDEX IF NOT EXISTS ix_candidate_identity ON candidate(package,identity_sha256,source_line)',
)


def apply_indexes(connection):
    for statement in INDEX_SQL:
        connection.execute(statement)
