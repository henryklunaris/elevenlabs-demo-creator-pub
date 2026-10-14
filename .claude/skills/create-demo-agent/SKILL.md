---
name: create-demo-agent
description: Build and deploy a live ElevenLabs demo agent for a client from a business name + website, and return the demo link. Use when the user wants a demo agent, demo link, or to spin up an agent for a business.
---

# Create Demo Agent

Goal: go from the user's first message to a working demo link as fast as possible. Don't interview the user.

## Step 1: Extract, don't ask

Pull everything you can from the user's message ($ARGUMENTS). Only ask (in ONE message) if the **website URL** is missing. Business name can be taken from the site if not given.

Use these defaults for anything not mentioned, and don't ask about them:

| Field | Default |
|-------|---------|
| Use case | Inbound customer service + FAQ |
| Voice | Female: Karen `AGYozmgYT0SJVnLKg7iN`. If the business is in AU use Emma `56bWURjYFHyYyVf490Dp`, UK use a British voice from `templates/elevenlabs/recommended-voices.md` |
| Agent name | Common first name matching the voice (e.g. Karen voice -> "Sarah") |
| First message | "Hi, this is {agent name} from {business}. This call may be recorded. How can I help you today?" |
| Language | `en` unless the site is clearly another language |

If the user describes a voice ("deep male British"), run `python3 scripts/el.py shared-voices --search "..." --gender ... --accent ...`, pick the best match, then `add-voice` it. Don't show options.

## Step 2: Scrape (one command, ~15s)

```bash
python3 scripts/scrape.py {url} {scratchpad}/{business-slug}-site.md
```

Picks up to 6 key pages (home, FAQ, services, pricing, about, contact) and scrapes them in parallel. Read the output file and pull out: services, pricing, hours, contact info, locations/service areas, FAQs.

## Step 3: Write the prompt

1. Read the closest template in `templates/` (default `customer-service.md`) and `platform-guides/elevenlabs.md`.
2. Write the prompt. First message has already been sent. Include role, business context, conversation flow, tone, call closure (use `end_call`), and `{{system__time}}` / `{{system__timezone}}`.
3. Add a `# Knowledge Base` section:
   - Scraped content under ~6000 chars: put all key info in the prompt.
   - Over that: put the essentials (contact, hours, areas, top services) in the prompt and say "Check the knowledge base for detailed service info and FAQs". The full scrape goes into RAG in Step 4.
4. Save to `output-prompts/{business-slug}-demo-elevenlabs-{YYYY-MM-DD}.md`.

## Step 4: Deploy

Run in one Bash call:

```bash
OUT=$(python3 scripts/el.py create-agent --name "{business} - Demo" \
  --prompt-file output-prompts/{file}.md \
  --first-message "{first message}" --voice-id {voice_id}) && echo "$OUT"
AID=$(echo "$OUT" | awk '/Created agent/{print $3}')
# Only if using RAG:
python3 scripts/el.py kb-add --text-file {scratchpad}/{business-slug}-site.md \
  --name "{business} - Website" --agent-id $AID
```

Defaults (Haiku 4.5, `eleven_v4_turbo`, `turn_v3`, 240s max) come from `templates/elevenlabs/agent-config.json`.

## Step 5: Reply

Keep it short:

```
**{Business} demo is live:** https://elevenlabs.io/app/talk-to?agent_id={agent_id}

{Agent name} ({voice name}), {use case}, knowledge base: {in prompt / RAG}
Prompt: output-prompts/{file}.md
```

Mention any defaults you picked in one line so the user can ask for changes. Changes later go through `python3 scripts/el.py update-agent {agent_id} ...`.

## Notes
- Never put time limits in the prompt. `max_duration_seconds` handles it.
- If the scrape fails, build the prompt from whatever the user gave and say the KB is thin.
