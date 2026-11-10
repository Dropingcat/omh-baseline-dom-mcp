"""Runner evidence reads must release Windows file handles deterministically."""
from contextlib import closing
import sqlite3
import pytest
from mockup.ab002_e2e import readback


def test_readback_closes_real_sqlite_connection_before_path_injection(tmp_path, monkeypatch):
    db = tmp_path / 'dom.sqlite3'
    with closing(sqlite3.connect(db)) as c:
        c.execute('CREATE TABLE marker(value BLOB)')
        c.execute('INSERT INTO marker VALUES(?)', (b'exact\r\n',))
        c.commit()
    original_connect = sqlite3.connect
    opened = []

    def tracked_connect(*args, **kwargs):
        c = original_connect(*args, **kwargs)
        opened.append(c)  # Do not allow GC to conceal missing explicit close.
        return c

    monkeypatch.setattr(sqlite3, 'connect', tracked_connect)
    result = readback(tmp_path, 'before-path-injection')
    assert result['tables']['marker'] == [[{'blob_hex': b'exact\r\n'.hex()}]]
    assert len(opened) == 1
    try:
        with pytest.raises(sqlite3.ProgrammingError, match='closed database'):
            opened[0].execute('SELECT 1')
        saved = tmp_path / 'saved-dom.sqlite3'
        db.rename(saved)
        saved.rename(db)
        assert readback(tmp_path, 'after-path-injection') == result
    finally:
        for c in opened:
            c.close()
