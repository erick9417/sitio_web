from __future__ import annotations

import hmac
import hashlib
import json
import os
import subprocess
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Deploy Webhook")

GITHUB_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
DEPLOY_SCRIPT = os.getenv('DEPLOY_SCRIPT', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'deploy', 'pull_and_restart.sh')))
DEPLOY_BRANCH = os.getenv('DEPLOY_BRANCH', 'main')


def _verify_signature(secret: str | None, payload: bytes, signature_header: str | None) -> bool:
    if not secret:
        return False
    if not signature_header:
        return False
    try:
        sha_name, signature = signature_header.split('=')
    except Exception:
        return False
    if sha_name != 'sha256':
        return False
    mac = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
    expected = mac.hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post('/webhook/github')
async def github_webhook(request: Request, x_hub_signature_256: str | None = Header(None), x_github_event: str | None = Header(None)) -> Any:
    body = await request.body()

    if not _verify_signature(GITHUB_SECRET, body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail='Invalid signature')

    try:
        payload = json.loads(body)
    except Exception:
        payload = {}

    # Only act on push to configured branch
    ref = payload.get('ref')
    if ref and ref != f'refs/heads/{DEPLOY_BRANCH}':
        return JSONResponse({'ok': False, 'reason': 'push to other branch, ignored'})

    # Run deploy script asynchronously
    try:
        # spawn background process
        subprocess.Popen(['/bin/bash', DEPLOY_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error launching deploy script: {e}')

    return JSONResponse({'ok': True, 'message': 'Deploy started'})
