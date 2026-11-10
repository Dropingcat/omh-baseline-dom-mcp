"""Local SQLite authority. All historical tables have SQL immutability triggers."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3

from .delivery import DDL as DELIVERY_DDL, KEYS as DELIVERY_KEYS

class MigrationRequired(Exception): pass

# WS-F02: idempotency v2 layout (extended PK + binding columns). Marker stored in
# PRAGMA user_version; a DB with the old layout and user_version >= this value is
# inconsistent and refuses (MIGRATION_REQUIRED, never a silent rebuild).
IDEMPOTENCY_SCHEMA_VERSION = 1

# AB006 (RS007 W1, option A): migration v2 — immutable candidate birthmark
# ``created_at`` plus the two join indexes the pending view needs
# (admitted-predicate on claims/idempotency). ``user_version`` is a monotone
# schema level: >= 2 means v2 is expected, so a v2-level DB whose candidates
# table lost ``created_at`` refuses (MIGRATION_REQUIRED) instead of silently
# rebuilding. Additive on legacy DBs; old rows keep created_at NULL (legacy →
# age_seconds omitted, never 0).
CANDIDATES_SCHEMA_VERSION = 2

# WR-ADD (L0+L1): migration v3 — additive ``reviews.review_level`` (NULL for rows
# written before v3; never backfilled, never guessed) plus the immutable
# ``project_root`` (D-01 root request/goal) and ``adoptions`` (D-02) tables.
# Same rule as v2: ``user_version`` is a monotone level; a v3-stamped DB that
# lost the column refuses (MIGRATION_REQUIRED) instead of being silently rebuilt.
SCHEMA_VERSION = 3

MIGRATION_V2_DDL = [
    "ALTER TABLE candidates ADD COLUMN created_at TEXT",
    "CREATE INDEX IF NOT EXISTS idx_idempotency_candidate ON idempotency(candidate_id)",
    "CREATE INDEX IF NOT EXISTS idx_claims_candidate ON claims(candidate)",
]

IMMUTABLE=('binding','candidates','claims','claim_snapshots','events','reviews','transactions','idempotency','outbox','delivery_events','project_root','adoptions')
# Every UNIQUE constraint of each immutable table.  ``INSERT OR REPLACE`` /
# ``OR IGNORE`` / plain ``REPLACE`` resolve a conflict by deleting the stored
# row, which the ``BEFORE DELETE`` trigger does not see while
# ``recursive_triggers`` is off (the default).  The conflict can be on the PK
# *or* on a secondary UNIQUE key, so both are guarded.
IMMUTABLE_KEYS={
    'binding':(('id',),('work_ref',)),
    'candidates':(('id',),),
    'claims':(('id',),),
    'claim_snapshots':(('claim_id',),),
    'events':(('seq',),('id',)),
    'reviews':(('id',),),
    'transactions':(('id',),('branch','revision')),
    'idempotency':(('external_work_ref','operation','key','scope_digest'),),
    'outbox':(('id',),('tx','kind','target')),
    'delivery_events':(('seq',),),
    'project_root':(('id',),),
    'adoptions':(('seq',),('new_work_ref','source_work_ref')),
}
DDL='''
CREATE TABLE IF NOT EXISTS binding(id INTEGER PRIMARY KEY CHECK(id=1), work_ref TEXT UNIQUE NOT NULL, policy TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS branch_heads(branch TEXT PRIMARY KEY, revision INTEGER NOT NULL CHECK(revision>=0));
CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload BLOB NOT NULL, author TEXT NOT NULL, root TEXT NOT NULL, branch TEXT NOT NULL REFERENCES branch_heads(branch), created_at TEXT);
CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY, candidate TEXT NOT NULL REFERENCES candidates(id), payload BLOB NOT NULL, review_level TEXT);
CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY, branch TEXT NOT NULL REFERENCES branch_heads(branch), revision INTEGER NOT NULL, receipt BLOB NOT NULL, UNIQUE(branch,revision));
CREATE TABLE IF NOT EXISTS claims(id TEXT PRIMARY KEY, candidate TEXT NOT NULL REFERENCES candidates(id), tx TEXT NOT NULL REFERENCES transactions(id), content_type TEXT NOT NULL, raw BLOB NOT NULL, raw_sha256 TEXT NOT NULL, encoding TEXT NOT NULL, media_type TEXT NOT NULL, source_ref TEXT NOT NULL, origin_branch TEXT NOT NULL, origin_version TEXT NOT NULL, payload BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL, tx TEXT NOT NULL REFERENCES transactions(id), claim_ref TEXT REFERENCES claims(id), branch TEXT NOT NULL, revision INTEGER NOT NULL, kind TEXT NOT NULL, payload BLOB NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claim_snapshots(claim_id TEXT PRIMARY KEY REFERENCES claims(id), tx TEXT NOT NULL REFERENCES transactions(id), branch TEXT NOT NULL, revision INTEGER NOT NULL, dependencies TEXT NOT NULL, review_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS idempotency(external_work_ref TEXT NOT NULL, operation TEXT NOT NULL, key TEXT NOT NULL, scope_digest TEXT NOT NULL DEFAULT '', digest TEXT NOT NULL, result BLOB NOT NULL, candidate_id TEXT, review_id TEXT, branch TEXT, result_scope TEXT, PRIMARY KEY(external_work_ref,operation,key,scope_digest));
CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, tx TEXT NOT NULL REFERENCES transactions(id), kind TEXT NOT NULL, target TEXT NOT NULL, branch TEXT NOT NULL, revision INTEGER NOT NULL, digest TEXT NOT NULL, payload BLOB NOT NULL, UNIQUE(tx,kind,target));
CREATE TABLE IF NOT EXISTS delivery_events(seq INTEGER PRIMARY KEY AUTOINCREMENT, intent TEXT NOT NULL REFERENCES outbox(id), state TEXT NOT NULL, payload BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS project_root(id INTEGER PRIMARY KEY CHECK(id=1), request_claim_id TEXT NOT NULL REFERENCES claims(id), goal_claim_id TEXT REFERENCES claims(id), goal_confirmed INTEGER NOT NULL DEFAULT 0 CHECK(goal_confirmed IN (0,1)), request_sha256 TEXT NOT NULL, goal_sha256 TEXT, branch TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS adoptions(seq INTEGER PRIMARY KEY AUTOINCREMENT, new_work_ref TEXT NOT NULL, source_work_ref TEXT NOT NULL, source_policy TEXT NOT NULL, chain_hash TEXT NOT NULL, user_version_at INTEGER NOT NULL, adopted_at TEXT NOT NULL, UNIQUE(new_work_ref,source_work_ref));
'''

class Store:
    def __init__(self,directory): self.path=Path(directory)/'dom.sqlite3'
    def connect(self):
        if getattr(self,'read_only',False):
            c=sqlite3.connect(self.path.as_uri()+'?mode=ro',uri=True,timeout=2,isolation_level=None)
        else: c=sqlite3.connect(self.path,timeout=2,isolation_level=None)
        c.row_factory=sqlite3.Row
        c.execute('PRAGMA foreign_keys=ON'); c.execute('PRAGMA synchronous=FULL'); c.execute('PRAGMA busy_timeout=2000')
        # Invariants are checked explicitly: ``assert`` would vanish under ``python -O``.
        if c.execute('PRAGMA foreign_keys').fetchone()[0]!=1: raise RuntimeError('PRAGMA_FOREIGN_KEYS_NOT_ENFORCED')
        if c.execute('PRAGMA synchronous').fetchone()[0]!=2: raise RuntimeError('PRAGMA_SYNCHRONOUS_NOT_FULL')
        return c
    def initialize(self,work,policy,branches=('AA','AB'),declare=(),adopt=None):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as c:
            if c.execute('PRAGMA journal_mode=DELETE').fetchone()[0]!='delete': raise RuntimeError('JOURNAL_MODE_NOT_DELETE')
            # Refuse incompatible legacy layouts before changing any schema.
            tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            required={'claims':{'id','content_type','encoding','media_type','source_ref'},
                      'claim_snapshots':{'claim_id','dependencies','review_id'},
                      'outbox':{'id','tx','kind','target','branch','revision','digest','payload'}}
            if tables and any(t not in tables or not cols <= {r[1] for r in c.execute('PRAGMA table_info('+t+')')} for t,cols in required.items()):
                raise MigrationRequired('MIGRATION_REQUIRED')
            # WS-F02 idempotency v2 migration (user_version gate): the old PK
            # (work,operation,key) makes a legal retry after a legacy refusal
            # impossible (UNIQUE/IMMUTABLE). Rebuild the table with the extended
            # PK; legacy rows become scope_digest='' + NULL binding (inert).
            if 'idempotency' in tables:
                cols={r[1] for r in c.execute('PRAGMA table_info(idempotency)')}
                if 'scope_digest' not in cols:
                    version=c.execute('PRAGMA user_version').fetchone()[0]
                    if version>=IDEMPOTENCY_SCHEMA_VERSION:
                        raise MigrationRequired('MIGRATION_REQUIRED')
                    c.execute('BEGIN IMMEDIATE')
                    try:
                        self._migrate_idempotency(c)
                        c.commit()
                    except BaseException:
                        c.rollback(); raise
            c.executescript(DDL+DELIVERY_DDL)
            self._create_triggers(c)
            # AB006 migration v2 (created_at + join indexes). Additive; idempotent
            # on re-run. The v2 level is monotone, so this must run before the
            # final user_version stamp below.
            cand_cols={r[1] for r in c.execute('PRAGMA table_info(candidates)')}
            if 'created_at' not in cand_cols:
                version=c.execute('PRAGMA user_version').fetchone()[0]
                if version>=CANDIDATES_SCHEMA_VERSION:
                    raise MigrationRequired('MIGRATION_REQUIRED')
                c.execute('BEGIN IMMEDIATE')
                try:
                    for stmt in MIGRATION_V2_DDL: c.execute(stmt)
                    c.commit()
                except BaseException:
                    c.rollback(); raise
                # Defensive re-creation (IF NOT EXISTS, idempotent): a future
                # table-rebuild step may drop triggers with the old table.
                self._create_triggers(c)
            else:
                # created_at already present (fresh DB or prior run): only the
                # indexes may still be missing on legacy copies — ensure them.
                for stmt in MIGRATION_V2_DDL[1:]: c.execute(stmt)
            # WR-ADD migration v3 (reviews.review_level). Additive, idempotent.
            review_cols={r[1] for r in c.execute('PRAGMA table_info(reviews)')}
            if 'review_level' not in review_cols:
                version=c.execute('PRAGMA user_version').fetchone()[0]
                if version>=SCHEMA_VERSION:
                    raise MigrationRequired('MIGRATION_REQUIRED')
                c.execute('BEGIN IMMEDIATE')
                try:
                    c.execute('ALTER TABLE reviews ADD COLUMN review_level TEXT')
                    c.commit()
                except BaseException:
                    c.rollback(); raise
                self._create_triggers(c)
            c.execute('BEGIN IMMEDIATE')
            try:
                row=c.execute('SELECT * FROM binding').fetchone()
                if row and (row['work_ref']!=work or row['policy']!=policy):
                    # D-02: a foreign base can only be taken over by an explicit,
                    # append-only adoption record naming the exact source work.
                    already=c.execute('SELECT 1 FROM adoptions WHERE new_work_ref=? AND source_work_ref=?',(work,row['work_ref'])).fetchone()
                    if already: pass
                    elif adopt and adopt.get('source_work')==row['work_ref']:
                        c.execute('INSERT INTO adoptions(new_work_ref,source_work_ref,source_policy,chain_hash,user_version_at,adopted_at) VALUES(?,?,?,?,?,?)',
                                  (work,row['work_ref'],row['policy'],adopt['chain_hash'],c.execute('PRAGMA user_version').fetchone()[0],adopt['at']))
                    else: raise ValueError('BINDING_CONFLICT')
                if not row:
                    c.execute('INSERT INTO binding VALUES(1,?,?)',(work,policy))
                    c.executemany('INSERT INTO branch_heads VALUES(?,0)',[(b,) for b in branches])
                for b in declare:
                    c.execute('INSERT OR IGNORE INTO branch_heads VALUES(?,0)',(b,))
                c.commit()
            except BaseException: c.rollback(); raise
            c.execute('PRAGMA user_version = %d' % SCHEMA_VERSION)
    def _create_triggers(self,c):
        for table in IMMUTABLE+tuple(DELIVERY_KEYS):
            for verb in ('UPDATE','DELETE'):
                c.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{verb} BEFORE {verb} ON {table} BEGIN SELECT RAISE(ABORT,'IMMUTABLE'); END")
            # R2-1: ``INSERT OR REPLACE`` resolves a PK/UNIQUE conflict by
            # deleting the stored row, and with ``recursive_triggers`` off
            # that delete never reaches the trigger above.  Refusing any
            # insert whose key already exists closes the REPLACE/IGNORE
            # path for every client: the guard is stored in the schema, so
            # it also applies to raw connections that never run
            # ``Store.connect()`` and never switch the PRAGMA on.
            parts=[]
            for key in (DELIVERY_KEYS.get(table) or IMMUTABLE_KEYS[table]):
                test=' AND '.join(f'{col}=NEW.{col}' for col in key)
                # ``seq`` is a rowid alias: undefined for an insert that
                # does not supply it, so that clause must also test not-null.
                if 'seq' in key: test='NEW.seq IS NOT NULL AND '+test
                parts.append(f'EXISTS(SELECT 1 FROM {table} WHERE {test})')
            c.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_INSERT BEFORE INSERT ON {table} "
                      f"WHEN {' OR '.join(parts)} BEGIN SELECT RAISE(ABORT,'IMMUTABLE'); END")
        # TD-DOM-12: branch_heads is mutable but MONOTONIC.  A rewind of the
        # head (UPDATE ... SET revision=lower) hides transactions already
        # stored and lets STALE_CHECK disappear, producing false readiness.
        # Block any decrease, and any head below the max transaction revision.
        c.execute("CREATE TRIGGER IF NOT EXISTS branch_heads_monotonic_update BEFORE UPDATE ON branch_heads "
                  "WHEN NEW.revision < OLD.revision "
                  "BEGIN SELECT RAISE(ABORT,'BRANCH_HEAD_REWIND'); END")
        c.execute("CREATE TRIGGER IF NOT EXISTS branch_heads_invariant_update BEFORE UPDATE ON branch_heads "
                  "WHEN NEW.revision < COALESCE((SELECT MAX(revision) FROM transactions WHERE branch=NEW.branch),0) "
                  "BEGIN SELECT RAISE(ABORT,'BRANCH_HEAD_BELOW_TX'); END")
        # A branch head may never be deleted: that would also hide history and
        # break the FK from transactions.
        c.execute("CREATE TRIGGER IF NOT EXISTS branch_heads_no_delete BEFORE DELETE ON branch_heads "
                  "BEGIN SELECT RAISE(ABORT,'BRANCH_HEAD_DELETE'); END")
        # Append-only chain guard: a new event must extend the stored hash chain.
        # It does not replace verification (see admission.verify_chain), it only
        # blocks inserts that do not continue the current chain state.
        c.execute("CREATE TRIGGER IF NOT EXISTS chain_previous_hash BEFORE INSERT ON events "
                  "BEGIN SELECT RAISE(ABORT,'CHAIN_INTEGRITY') WHERE NEW.previous_hash <> "
                  "COALESCE((SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1),'" + '0' * 64 + "'); END")
    def _migrate_idempotency(self,c):
        # Destructive rebuild of the immutable idempotency table (extended PK):
        # legacy rows are copied as-is with scope_digest='' and NULL binding --
        # never rewritten, never served, never deleted. Immutable triggers are
        # dropped with the old table and recreated by initialize() afterwards.
        c.execute('CREATE TABLE idempotency_v2(external_work_ref TEXT NOT NULL, operation TEXT NOT NULL, '
                  "key TEXT NOT NULL, scope_digest TEXT NOT NULL DEFAULT '', digest TEXT NOT NULL, "
                  'result BLOB NOT NULL, candidate_id TEXT, review_id TEXT, branch TEXT, result_scope TEXT, '
                  'PRIMARY KEY(external_work_ref,operation,key,scope_digest))')
        c.execute("INSERT INTO idempotency_v2(external_work_ref,operation,key,scope_digest,digest,result) "
                  "SELECT external_work_ref,operation,key,'',digest,result FROM idempotency")
        c.execute('DROP TABLE idempotency')
        c.execute('ALTER TABLE idempotency_v2 RENAME TO idempotency')
        c.execute('PRAGMA user_version = %d' % IDEMPOTENCY_SCHEMA_VERSION)
    @contextmanager
    def transaction(self):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE'); yield c; c.commit()
        except BaseException: c.rollback(); raise
        finally: c.close()
    @contextmanager
    def read(self):
        c=self.connect()
        try:
            c.execute('BEGIN'); yield c
        finally:
            c.rollback(); c.close()
