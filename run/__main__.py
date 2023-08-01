"""Starts the API.

Usage:
$ python run 1234
Runs on port 1234.

$ python run prod
Runs for production.

$ python run 1234 prod
Runs for production on the speicified port.

"""

import os
import sys

port = sys.argv[1] if len(sys.argv) > 1 else 2332
dev = True

if 'prod' in sys.argv:
    port = 2333
    dev = False

os.system(f'cd api && uvicorn main:app{" --reload" if dev else ""} --host 0.0.0.0 --port {port}')
