# Voice AI Prompt Builder

## What This Is

A prompt engineering workspace for ElevenLabs voice AI agents. The user types what they need, you generate
a production-ready system prompt and can deploy it as an agent via `scripts/el.py`.

## Project Layout

templates/           - Example prompt templates by use case
templates/elevenlabs/ - Voices list + agent-config.json (base config for new agents)
platform-guides/     - elevenlabs.md (platform conventions and current defaults)
scripts/el.py        - ElevenLabs API CLI (agents, knowledge base, voices, calls)
scripts/scrape.py    - Firecrawl v2 parallel site scraper -> one markdown file
output-prompts/      - Generated prompts land here
.claude/skills/      - Automated skills (create-demo-agent, generate-prompt)

## Integrations

- **Firecrawl**: Website scraping API. Key in `.env` as `FIRECRAWL_API_KEY`. Used by `create-demo-agent` to scrape client sites.
- **ElevenLabs API**: Key in `.env` as `ELEVENLABS_API_KEY`. No MCP. Use `python3 scripts/el.py -h` for all commands (create-agent, update-agent, get-agent, list-agents, kb-add, kb-attach, kb-list, voices, shared-voices, add-voice, phones, call).

## Rules
- Lazy file reading. Only read files you need, match by filename first.
- Output always goes to output-prompts/ with the naming convention: {description}-{platform}-{YYYY-MM-DD}.md
- Templates and platform guides are reference material, use them as structural inspiration.
- Ask one question at a time, don't overwhelm the user.
- Always collect the business name if you don't have it.
