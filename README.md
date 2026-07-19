# DataForge AI

AI-powered Dataset Engineering IDE for inspecting, cleaning, and improving tabular ML datasets.

## Stack

- **Backend:** Python 3.12, FastAPI, pandas, scikit-learn
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **AI:** OpenAI API for explanations and repair recommendations
- **Dev:** GitHub Codespaces (`.devcontainer/`)

## Quick start (Codespaces)

1. Push this repo to GitHub.
2. Open **Code → Codespaces → Create codespace on main**.
3. After the post-create script finishes, add your API key to `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ```
4. In two terminals:
   ```bash
   make backend   # http://localhost:8000
   make frontend  # http://localhost:5173
   ```
5. Open the forwarded **Frontend** port in the browser.

API docs: `http://localhost:8000/docs`

## Project phases

| Phase | Goal |
|-------|------|
| **0** | Repo, devcontainer, health checks ✅ |
| **1** | Upload CSV + profile + issue detection ✅ |
| **2** | AI explanations + repair recommendations (OpenAI) ✅ |
| **3** | Apply repairs + version history |
| **4** | Export dataset, pipeline, quality report |

## Local development (without Codespaces)

Requires Python 3.12+ and Node 20+.

```bash
cp .env.example .env
make install
make backend   # terminal 1
make frontend  # terminal 2
```

## License

MIT
