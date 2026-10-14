# Demo Builder 

## Setup

### Hostinger
https://hostinger.com/henryk10

### Claude Code (Terminal)
After copying repo:
  ```
1. Ask for a prompt:
  ```
   give me a prompt for an inbound FAQ agent for Acme Corp
  ```
2. Add `ELEVENLABS_API_KEY` and `FIRECRAWL_API_KEY` to `.env` to deploy agents and scrape sites.

#### Firecrawl
https://www.firecrawl.dev/

#### Elevenlabs
https://elevenlabs.io/

### Cursor

1. Clone the repo and open it in Cursor
2. The `CLAUDE.md` file will automatically give the agent context
3. Open the chat and ask for a prompt — same as above



## Usage

Just describe what you need in plain language:

- `"build me an appointment booking agent for a dental clinic"`
- `"I need an outbound lead gen prompt for a SaaS company"`
- `/create-demo-agent` to scrape a client site and deploy a live demo agent

The agent will ask a few clarifying questions, match your use case to a template, apply ElevenLabs conventions, and save the result to `output-prompts/`.

## ElevenLabs Scripts

`scripts/el.py` talks to the ElevenLabs API directly (no MCP, no pip installs):

```bash
python3 scripts/el.py create-agent --name "Acme - FAQ" --prompt-file output-prompts/acme.md --first-message "Hi..." --voice-id AGYozmgYT0SJVnLKg7iN
python3 scripts/el.py update-agent <agent_id> --prompt-file output-prompts/acme.md
python3 scripts/el.py kb-add --text-file site.txt --name "Acme site" --agent-id <agent_id>
python3 scripts/el.py shared-voices --search "warm british" --gender female
```

Base agent settings live in `templates/elevenlabs/agent-config.json`.

## Adding Templates

Drop a new `.md` file in `templates/` following the existing structure (Role, Rules, Context, Call Flow, Communication Rules, etc.). The agent will automatically pick it up when it matches a user's request.

