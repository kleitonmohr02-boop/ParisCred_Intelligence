# OpenCode Power Setup Guide

## Completed ✅
- [x] OpenCode v1.3.2 installed
- [x] Configuration file created at `~/.opencode/opencode.json`
- [x] Skills installed:
  - python-expert
  - architecture-expert
  - security-best-practices

## To Complete (Manual Steps)

### 1. Get Gemini API Key (FREE)
1. Go to: https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Create a `.env` file or set environment variable:
   ```bash
   # Windows
   setx GOOGLE_API_KEY "your_key_here"
   
   # Or create .env file in project root
   GOOGLE_API_KEY=your_key_here
   ```

### 2. Install Ollama (Optional - for local models)
Download from: https://ollama.com/download

Then run:
```bash
ollama pull qwen3:8b
ollama pull deepseek-coder:6.7b
```

### 3. Verify Setup
```bash
opencode --version
opencode /models  # To see available models
```

### 4. Test Gemini
```bash
opencode
# Then type: "Hello, test my configuration"
```

## Current Configuration
- Primary Model: `google/gemini-2.5-flash` (with thinking enabled)
- Fallback: `google/gemini-2.0-flash`
- Skills: Python Expert, Architecture, Security

## Tips
- Gemini 2.5 Flash is FREE (250 req/day)
- Use thinking mode for complex tasks
- Skills auto-load for relevant context
