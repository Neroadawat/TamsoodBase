"""Run inside the API container; prove grants and transaction deny mutations."""
import json
from src.mysql_store import connect

con=connect()
try:
    with con.cursor() as cur:
        cur.execute('SHOW GRANTS')
        grants=[next(iter(row.values())) for row in cur.fetchall()]
        if any('ALL PRIVILEGES' in g or 'GRANT OPTION' in g for g in grants):
            raise RuntimeError('Reader has excessive privileges')
        if any(not (g.startswith('GRANT SELECT ON ') or g.startswith('GRANT USAGE ON ')) for g in grants):
            raise RuntimeError('Reader has non-read grants')
        try:
            cur.execute("UPDATE artifact SET name=name WHERE name='runtime_info'")
        except Exception as e:
            if e.args[0] not in (1142,1792):raise
            print(json.dumps({'passed':True,'select_only_grants':True,'write_denied':True,'error_code':e.args[0]}))
        else:raise RuntimeError('Reader unexpectedly allowed UPDATE')
finally:
    con.rollback();con.close()
