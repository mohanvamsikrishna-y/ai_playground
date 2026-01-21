# AI Model Comparison Playground

A modern chat interface for comparing multiple AI models side-by-side. Supports local Ollama models and cloud providers (Gemini, DeepSeek) with Bring-Your-Own-Key (BYOK) authentication.

## Features

- **Multi-model chat**: Compare responses from multiple models simultaneously
- **Local models**: Use Ollama models on your machine (local mode only)
- **Cloud providers**: Support for Gemini and DeepSeek via BYOK
- **Modern UI**: Clean chat interface with tabs, sidebar, and fixed input
- **Secure**: API keys stored only in browser localStorage, never on server

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

### Frontend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

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
