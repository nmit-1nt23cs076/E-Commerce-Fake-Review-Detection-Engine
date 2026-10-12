import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import uvicorn
from config import PORT, HOST

if __name__ == "__main__":
    print(f"[*] Launching ReviewGuard AI Server at http://{HOST}:{PORT} ...")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
