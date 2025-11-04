Deploy webhook and script
=========================

This folder contains a minimal deploy script and instructions to wire GitHub pushes to a server.

Files
- `pull_and_restart.sh` - shell script that pulls the repository and restarts a systemd service. It expects the repo to be present on the server.

How it works (quick)
1. Create a GitHub webhook in your repository settings pointing to `https://your-server.example.com/webhook/github`.
   - Use `application/json` as content type
   - Set a secret and add it to the server's environment variable `GITHUB_WEBHOOK_SECRET`.
2. On the server, make sure the repository is checked out (the script uses the deploy folder path).
3. Make sure the `pull_and_restart.sh` script is executable:

```bash
chmod +x backend/deploy/pull_and_restart.sh
```

4. Configure your service name in environment variable `DEPLOY_SERVICE`, for example `api.service`, or edit the script.
5. Run a FastAPI app that exposes `/webhook/github` (we provide an example in `backend/api/webhook_app.py`).

Security notes
- Always use the webhook secret; the webhook endpoint validates `X-Hub-Signature-256`.
- Run the webhook endpoint behind HTTPS (use a reverse proxy like nginx and a TLS certificate).
- Limit access via firewall or trusted IPs if possible.
