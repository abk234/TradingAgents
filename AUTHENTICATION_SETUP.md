# Authentication Setup Guide

## Overview
The TradingAgents application now includes API Key-based authentication to protect your intellectual property and restrict access to authorized users only.

## Your Generated API Key
```
Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg
```

**IMPORTANT**: Keep this key secure and do not share it publicly.

## Setup Instructions

### 1. Add API Key to Environment Variables

Open your `.env` file (or create one from `.env.example`) and add:

```bash
API_KEY=Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg
```

### 2. Restart the Backend Server

After adding the API key to your `.env` file, restart the backend:

```bash
# If using start_fresh.sh
./start_fresh.sh

# Or manually restart the backend
pkill -f "uvicorn tradingagents.api.main"
python -m uvicorn tradingagents.api.main:app --host 0.0.0.0 --port 8005
```

### 3. Access the Web Application

1. Navigate to `http://localhost:3005` (or your configured frontend URL)
2. You will be redirected to the login page
3. Enter the API key: `Uo8m722b5pkY4s8ixSqm3SkIGXcVR55JkjUm4cNaUlg`
4. Click "Login" to access the dashboard

## How It Works

### Backend (FastAPI)
- All API endpoints (except `/health`, `/`, and `/metrics`) require the `X-API-Key` header
- The middleware validates the key against the `API_KEY` environment variable
- Invalid or missing keys receive a `401 Unauthorized` response

### Frontend (Next.js)
- The login page stores the API key in `localStorage`
- The `AuthProvider` manages authentication state
- All API requests automatically include the `X-API-Key` header
- Unauthenticated users are redirected to `/login`

## Development Mode

If no `API_KEY` is set in the environment, the backend will allow all requests (development mode). This is useful for local testing but **should never be used in production**.

## Generating a New API Key

If you need to generate a new API key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Update the `.env` file with the new key and restart the backend.

## Security Best Practices

1. **Never commit** your `.env` file to version control
2. **Use different keys** for development, staging, and production
3. **Rotate keys regularly** (e.g., every 90 days)
4. **Store keys securely** using a password manager or secrets management service
5. **Monitor access logs** for unauthorized attempts

## IP Protection

In addition to authentication, the application includes:

1. **License Headers**: All source files now include copyright and license information
2. **Footer**: The web UI displays copyright notice and version information
3. **Apache License 2.0**: The project is licensed under Apache 2.0 (see LICENSE file)

## Troubleshooting

### "Unauthorized" Error
- Verify the API key in your `.env` file matches the one you're using to login
- Ensure the backend has been restarted after updating `.env`
- Check that the API key doesn't have extra spaces or newlines

### Login Page Not Showing
- Clear your browser's localStorage: `localStorage.clear()`
- Hard refresh the page (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

### API Key Not Working
- Check the browser console for errors
- Verify the `X-API-Key` header is being sent (use browser DevTools Network tab)
- Ensure the backend is running and accessible
