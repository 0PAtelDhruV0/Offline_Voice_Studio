# Optional neural voice server

GitHub Pages cannot run Python. This optional backend uses Edge neural speech and requires internet access; it is not an official supported Microsoft API and may stop working.

## Start locally (Windows)
Install Python 3.11+, then in this folder:

```powershell
pip install -r requirements.txt
$env:ALLOWED_ORIGIN="https://0pateldhruv0.github.io"
uvicorn server:app --host 127.0.0.1 --port 8787
```

For iPad access, deploy this backend to an HTTPS Python hosting service and set ALLOWED_ORIGIN to https://0pateldhruv0.github.io. Put the public HTTPS backend URL into Voice Studio's Server field, select Neural, and press Generate audio. A locally hosted HTTP URL will not work from the HTTPS GitHub Pages site.

Security: This example has no user authentication or usage quotas; do not expose it publicly without access controls, rate limits, and abuse protection. It also needs a deployment fix for file lifetime before production use.

The offline fallback is the browser's built-in speech engine. It does not require this server.
