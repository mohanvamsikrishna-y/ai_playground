# AI Model Comparison Playground

A modern chat interface for comparing multiple AI models side-by-side. Supports local Ollama models and cloud providers (Gemini, DeepSeek) with Bring-Your-Own-Key (BYOK) authentication.

## Features

- **Multi-model chat**: Compare responses from multiple models simultaneously
- **Local models**: Use Ollama models on your machine (local mode only)
- **Cloud providers**: Support for Gemini and DeepSeek via BYOK
- **Modern UI**: Clean chat interface with tabs, sidebar, and fixed input
- **Secure**: API keys stored only in browser localStorage, never on server
- **Google Login**: Optional Google OAuth sign-in via NextAuth
- **Analytics**: Optional PostHog event tracking (frontend + backend)

## Deployment Modes

This project supports two deployment modes using the same codebase:

### Mode A: Local Self-Host Mode

- Full Ollama support (download and use any model)
- BYOK API keys stored in browser localStorage
- Works on Mac/Windows/Linux
- Best for: Personal use, development, testing

### Mode B: Hosted Cloud Mode

- Cloud providers only (Gemini, DeepSeek)
- Ollama features disabled
- BYOK API keys stored in browser localStorage
- Best for: Public demos, cloud deployments

## Quick Start (Local Mode)

### Prerequisites

- Docker and Docker Compose
- Ollama installed and running (for local models)
  - Download from [ollama.ai](https://ollama.ai)
  - Or use `docker-compose.ollama.yml` on Linux

#### macOS (with Homebrew)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install core tools
brew install git
brew install --cask docker
brew install --cask ollama

# Start Docker Desktop and Ollama (may require manual first launch/permissions)

# Clone and run the playground
git clone https://github.com/mohanvamsikrishna-y/ai_playground.git
cd ai_playground
cp .env.example .env
docker compose up --build
```

#### Windows 11 (PowerShell + Winget)

Run this in **PowerShell as Administrator**:

```powershell
# Install core tools (may prompt you through installers)
winget install -e --id Git.Git
winget install -e --id Docker.DockerDesktop
winget install -e --id Ollama.Ollama

# You may need to log out/in or restart after Docker Desktop installs.

# Clone and run the playground
git clone https://github.com/mohanvamsikrishna-y/ai_playground.git
cd ai_playground
copy .env.example .env
docker compose up --build
```

#### Linux (Ubuntu/Debian-like)

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin

# Optional: install Ollama for local models
curl -fsSL https://ollama.com/install.sh | sh

# Make sure your user can run Docker without sudo (may require re-login)
sudo usermod -aG docker "$USER"

# Clone and run the playground
git clone https://github.com/mohanvamsikrishna-y/ai_playground.git
cd ai_playground
cp .env.example .env
docker compose up --build
```

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_playground
   ```

2. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

3. **Start services**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Using Ollama Models

1. **Start Ollama** (if not already running)
   - Mac/Windows: Run Ollama desktop app
   - Linux: Use `docker compose -f docker-compose.yml -f docker-compose.ollama.yml up`

2. **Download models in the app**
   - Open the sidebar (click the toggle button if hidden)
   - Scroll to "Add Local Model (Ollama)" section
   - Enter a model name (e.g., `llama3.2`, `mistral`, `qwen2.5`)
   - Click "Download"
   - The model will appear in the model selector automatically

3. **Start chatting**
   - Select one or more models
   - Type your message in the input at the bottom
   - Press Enter or click "Send"

### Using Cloud Providers

1. **Add API keys**
   - Open the sidebar
   - Scroll to "Gemini Settings" or "DeepSeek Settings"
   - Paste your API key
   - Click "Save"
   - Keys are stored only in your browser

2. **Select models**
   - Cloud models appear automatically when keys are configured
   - Select them from the model selector

## Environment Variables

### Backend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PLAYGROUND_ENV` | Environment mode: `"local"` or `"prod"` | `None` (treated as local) |
| `PLAYGROUND_CORS_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000,http://127.0.0.1:3000` |
| `PLAYGROUND_OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `PLAYGROUND_GEMINI_API_KEY` | Optional server-side Gemini key | `None` |
| `PLAYGROUND_DEEPSEEK_API_KEY` | Optional server-side DeepSeek key | `None` |

| `PLAYGROUND_GOOGLE_CLIENT_ID` | Google OAuth client ID (for token verification) | `None` |
| `PLAYGROUND_POSTHOG_KEY` | PostHog project API key (server-side analytics) | `None` |

### Frontend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `AUTH_SECRET` | NextAuth session encryption secret | **Required for auth** |
| `AUTH_GOOGLE_ID` | Google OAuth client ID | **Required for auth** |
| `AUTH_GOOGLE_SECRET` | Google OAuth client secret | **Required for auth** |
| `NEXT_PUBLIC_POSTHOG_KEY` | PostHog project API key (frontend events) | `None` |
| `NEXT_PUBLIC_POSTHOG_HOST` | PostHog API host | `https://us.i.posthog.com` |

## Docker Compose Options

### Standard Setup (Mac/Windows)

```bash
docker compose up --build
```

Uses `host.docker.internal` to access Ollama running on your host machine.

### Linux Setup (with Ollama in Docker)

```bash
docker compose -f docker-compose.yml -f docker-compose.ollama.yml up --build
```

Includes Ollama as a Docker service. Update `.env`:
```
PLAYGROUND_OLLAMA_BASE_URL=http://ollama:11434
```

## BYOK (Bring Your Own Key)

API keys for cloud providers are stored **only in your browser's localStorage**. They are:

- ✅ Never sent to the server except in request headers
- ✅ Never stored on the server
- ✅ Never logged
- ✅ Browser-specific (not synced across devices)

### Adding Keys

1. Open Settings sidebar
2. Find provider section (Gemini/DeepSeek)
3. Paste your API key
4. Click "Save"
5. Keys persist across page refreshes

### Clearing Keys

Click "Clear Key" button in Settings to remove stored keys.

## Production Deployment

For production (cloud-only) deployment:

1. Set `PLAYGROUND_ENV=prod` in environment
2. Ollama endpoints will return 403 Forbidden
3. `/models` endpoint excludes Ollama models
4. Frontend automatically hides Ollama download UI

### Example (Cloud Run)

```bash
export PLAYGROUND_ENV=prod
export PLAYGROUND_CORS_ORIGINS=https://your-domain.com
# Deploy to Cloud Run
```

## Google OAuth Setup (Optional)

Google Login is optional. The app works without it — compare and models remain fully public.

### 1. Create Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Add **Authorized redirect URIs**:
   - Local: `http://localhost:3000/api/auth/callback/google`
   - Production: `https://your-frontend-url/api/auth/callback/google`
7. Copy the **Client ID** and **Client Secret**

### 2. Set environment variables

**Frontend** (`.env.local` or deployment env):
```bash
AUTH_SECRET=$(openssl rand -base64 32)
AUTH_GOOGLE_ID=<your-google-client-id>
AUTH_GOOGLE_SECRET=<your-google-client-secret>
```

**Backend** (env or `.env`):
```bash
PLAYGROUND_GOOGLE_CLIENT_ID=<your-google-client-id>
```

The backend uses the client ID to verify Google ID tokens sent by the frontend in `Authorization: Bearer <id_token>` headers.

### 3. Test

1. Start the app
2. Click "Sign in with Google" in the sidebar
3. Complete the Google OAuth flow
4. Your avatar and name should appear in the sidebar
5. Hit `GET /auth/me` with the token to verify backend verification works

## Analytics Setup (Optional)

Analytics are powered by [PostHog](https://posthog.com/) and are completely optional. No events are sent unless PostHog keys are configured.

### 1. Create a PostHog project

1. Sign up at [posthog.com](https://posthog.com/)
2. Create a project
3. Copy the **Project API Key** from Settings > Project

### 2. Set environment variables

**Frontend** (for browser-side events):
```bash
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com  # optional, defaults to US cloud
```

**Backend** (for server-side events — optional):
```bash
PLAYGROUND_POSTHOG_KEY=phc_xxx
```

### 3. Tracked events

| Event | Source | Properties |
|-------|--------|------------|
| `playground_opened` | Frontend | — |
| `model_selected` | Frontend | `model_id`, `model_provider`, `selected` |
| `chat_sent` | Frontend | `model_id`, `model_provider` |
| `response_received` | Frontend | `model_id`, `latency_ms`, `success` |
| `error_occurred` | Frontend | `model_id`, `error` |
| `compare_request_received` | Backend | `model_ids`, `model_count` |
| `compare_request_completed` | Backend | `model_ids`, `success_count`, `error_count`, `latency_ms` |

Prompts and responses are **never** logged or sent to analytics.

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React, TypeScript)
- **Styling**: Tailwind CSS, shadcn/ui components
- **State Management**: React hooks
- **API Communication**: Fetch API with custom error handling

## Project Structure

```
ai_playground/
├── backend/
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Model clients
│   │   └── config.py     # Configuration
│   └── Dockerfile
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/        # React components
│   ├── lib/              # API client, types
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.ollama.yml
└── .env.example
```

## Troubleshooting

### Ollama not found

- **Error**: "Ollama is not running. Start Ollama to use local models."
- **Solution**: Start Ollama desktop app or use `docker-compose.ollama.yml`

### Models not appearing

- Check that Ollama is running and accessible
- Verify `PLAYGROUND_OLLAMA_BASE_URL` is correct
- Check browser console for errors

### CORS errors

- Verify `PLAYGROUND_CORS_ORIGINS` includes your frontend URL
- Check that backend and frontend URLs match your setup

### API keys not working

- Verify keys are saved in browser localStorage
- Check browser console for API errors
- Ensure keys are valid and have proper permissions

## License

[Add your license here]
