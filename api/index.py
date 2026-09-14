import os
import sys

# Ensure repository root is in python path for serverless imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minesword.server import MineswordServer

# On Vercel / serverless platforms, local disk is read-only except /tmp
db_path = "/tmp/minesword.db" if os.getenv("VERCEL") or not os.access(".", os.W_OK) else "minesword.db"

app = MineswordServer(db_path=db_path)
