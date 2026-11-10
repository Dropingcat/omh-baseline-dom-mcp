"""Trusted SIMULATION test adapter, never an MCP tool or production launcher."""
import argparse
import os
from pathlib import Path
import anyio
from .admission import Service
from . import ports
from .server import serve


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--directory',required=True)
    p.add_argument('--role',default='reviewer')
    p.add_argument('--mode',default='available',choices=['available','liar','unavailable','ambiguous'])
    p.add_argument('--crash',default='')
    p.add_argument('--read-only',action='store_true')
    a=p.parse_args()
    service=Service(a.directory,role=a.role)
    service.store.read_only=a.read_only
    service.directory.mkdir(parents=True,exist_ok=True)
    service.omh_mode=a.mode
    if a.mode=='liar':
        ports.OMHPort.attach=lambda *args,**kwargs: 'ack'
    def hook(stage):
        if stage==a.crash:
            (service.directory/('crash-'+stage+'.json')).write_text(
                '{"pid":%d,"stage":"%s","exit":71}'%(os.getpid(),stage),encoding='utf8')
            os._exit(71)
    service.fault_hook=hook
    anyio.run(serve,service,None)


if __name__=='__main__': main()
