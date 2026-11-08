-- Local release-workflow candidate. Scientific approval is a separate gate.
PRAGMA foreign_keys=ON;
CREATE TABLE review_release(id TEXT PRIMARY KEY, content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64), scope TEXT NOT NULL CHECK(scope IN ('PUBLIC_METADATA','INTERNAL_ACTIVITY_REVIEW')), state TEXT NOT NULL DEFAULT 'DRAFT' CHECK(state IN ('DRAFT','IN_REVIEW','PUBLISHED','RETRACTED')), revision INTEGER NOT NULL DEFAULT 0);
CREATE TABLE review_event(event_id INTEGER PRIMARY KEY, release_id TEXT NOT NULL REFERENCES review_release, from_state TEXT NOT NULL,to_state TEXT NOT NULL, actor TEXT NOT NULL CHECK(length(trim(actor))>0), role TEXT NOT NULL, evidence_sha256 TEXT NOT NULL CHECK(length(evidence_sha256)=64), reason TEXT NOT NULL CHECK(length(trim(reason))>0), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TRIGGER immutable_event_update BEFORE UPDATE ON review_event BEGIN SELECT RAISE(ABORT,'Append-only audit'); END;
CREATE TRIGGER immutable_event_delete BEFORE DELETE ON review_event BEGIN SELECT RAISE(ABORT,'Append-only audit'); END;
CREATE TRIGGER immutable_release_identity BEFORE UPDATE OF id,content_sha256,scope ON review_release BEGIN SELECT RAISE(ABORT,'Content identity immutable'); END;
CREATE TRIGGER no_release_delete BEFORE DELETE ON review_release BEGIN SELECT RAISE(ABORT,'Retain release history'); END;
CREATE TRIGGER controlled_transition BEFORE UPDATE OF state,revision ON review_release
WHEN NOT (NEW.revision=OLD.revision+1 AND EXISTS(SELECT 1 FROM review_event WHERE release_id=OLD.id AND event_id=(SELECT max(event_id) FROM review_event WHERE release_id=OLD.id) AND from_state=OLD.state AND to_state=NEW.state))
BEGIN SELECT RAISE(ABORT,'Transition needs matching audit event'); END;
