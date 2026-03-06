# Security Rules

- Never hardcode API keys, tokens, or secrets in any file
- API keys belong in environment variables only
- If a key is found in code, flag it immediately
- Anthropic API key must route through Vercel edge proxy, never exposed client-side
- CORS enforced to deployed domain only
