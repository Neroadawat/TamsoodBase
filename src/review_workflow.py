"""Local metadata workflow contract; it does not approve LCI science or grant rights."""
ALLOWED={('DRAFT','IN_REVIEW'):'editor',('IN_REVIEW','DRAFT'):'reviewer',('IN_REVIEW','PUBLISHED'):'reviewer',('PUBLISHED','RETRACTED'):'reviewer'}
def transition(conn,release_id,target,expected_revision,*,actor,role,evidence_sha256,reason,rights_cleared=False,scientific_claim=False):
    if scientific_claim:raise ValueError('This workflow cannot approve full LCI or LCIA')
    if not actor or not actor.strip() or len(evidence_sha256)!=64 or not all(c in '0123456789abcdef' for c in evidence_sha256) or not reason.strip():raise ValueError('Actor, evidence hash and reason required')
    with conn:
        row=conn.execute('SELECT state,revision,scope FROM review_release WHERE id=?',(release_id,)).fetchone()
        if not row or row[1]!=expected_revision:raise ValueError('Stale or missing release')
        if ALLOWED.get((row[0],target))!=role:raise ValueError('Transition or role not allowed')
        if target=='PUBLISHED' and row[2]=='PUBLIC_METADATA' and not rights_cleared:raise ValueError('Public metadata needs its distribution review')
        if target=='PUBLISHED' and row[2]=='INTERNAL_ACTIVITY_REVIEW':raise ValueError('Internal research may not be published through this workflow')
        conn.execute('INSERT INTO review_event(release_id,from_state,to_state,actor,role,evidence_sha256,reason) VALUES(?,?,?,?,?,?,?)',(release_id,row[0],target,actor,role,evidence_sha256,reason))
        conn.execute('UPDATE review_release SET state=?,revision=revision+1 WHERE id=? AND revision=?',(target,release_id,expected_revision))
