---
name: generate-prompt
description: Generate a voice AI agent system prompt. Use when the user wants to create, build, or write a voice AI prompt or agent prompt for any platform.
---

# Generate Voice AI Prompt

## Step 1: Info Gathering
Start with a couple simple questions (under 15 words).
Then extract what you can from the user's response and only ask follow-ups for missing pieces.

Based on the user's request ($ARGUMENTS), try to identify:
- Setup type: inbound or outbound?
- Business context: industry, company name, main services
- Agent jobs: the 1-3 main tasks this agent handles
- Use case: customer service, appointment booking, lead gen, etc.

If the niche or platform is ambiguous, ask. Don't guess.
One question at a time. Be conversational.

## Step 2: Match Template
1. List filenames in `templates/`
2. Pick the best match for the user's niche
3. Read only the matched template
4. If no match, pick the closest one for structural inspiration

Do NOT read all templates. Only read the one that matches.

## Step 3: Read Platform Guide
Read `platform-guides/elevenlabs.md`.

## Step 4: Generate the Prompt
Using the matched template + platform guide + gathered info:
- Generate a complete system prompt tailored to the niche
- Follow the platform guide conventions (time variables, function names, call ending, etc.)
- Adapt the template structure to the specific business
- Include: Role, Context, Conversation Flow, Handling Queries, Tone, Call Closure, Notes

## Step 5: Save Output
Save to: `output-prompts/{description}-elevenlabs-{YYYY-MM-DD}.md`

Present the full prompt to the user and confirm the file was saved. Offer to push it live with `python3 scripts/el.py create-agent ...` or `update-agent {agent_id} --prompt-file ...`.
