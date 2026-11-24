"""Serve a prebuilt Asset Studio offline; standard library only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    directory=Path(__file__).resolve().parent
    if not (directory/"live_catalog.json").is_file():
        parser.error("Extract the prepared Studio ZIP before starting this server")
    handler=partial(SimpleHTTPRequestHandler,directory=str(directory))
    with ThreadingHTTPServer(("127.0.0.1",args.port),handler) as server:
        print(f"Asset Studio offline: http://127.0.0.1:{args.port}/",flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
if __name__=="__main__":
    main()
