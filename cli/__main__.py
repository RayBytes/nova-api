import sys
import os

port = sys.argv[1] if len(sys.argv) > 1 else 8000
os.system(f'cd api && uvicorn main:app --reload --host 0.0.0.0 --port {port}')
