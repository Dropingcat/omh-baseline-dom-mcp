"""Second OS process owns the write lock until runner releases it."""
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

def main():
    d=Path(sys.argv[1]).resolve()
    runtime=Path(__file__).resolve().parents[1]/'runtime'
    if not d.is_relative_to(runtime): raise SystemExit('RUNTIME_PATH_REQUIRED')
    with sqlite3.connect(d/'dom.sqlite3',isolation_level=None) as c:
        c.execute('BEGIN IMMEDIATE')
        (d/'lock-ready.json').write_text(json.dumps({'pid':os.getpid(),'lock':'BEGIN IMMEDIATE'}),encoding='utf8')
        deadline=time.monotonic()+60
        while not (d/'lock-release').exists():
            if time.monotonic()>deadline: raise TimeoutError('lock owner timeout')
            time.sleep(.02)
        c.rollback()

if __name__=='__main__': main()
