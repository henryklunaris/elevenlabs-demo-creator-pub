# ElevenLabs Agents

Docs: https://elevenlabs.io/docs/eleven-agents (API paths still use `/v1/convai/`)

## Variables
- `{{system__time}}` current time, `{{system__timezone}}` agent timezone (set in `agent.prompt.timezone`)
- `{{system__caller_id}}` caller number on phone calls
- Custom dynamic variables use `{{name}}` and need a placeholder in `agent.dynamic_variables`

## Tools
- `end_call` system tool ends the call. In prompts, tell the agent to "use the end_call tool" when the conversation is done.
- `skip_turn` lets the agent stay quiet when the caller says "hold on" or similar.
- Other built-ins (set in `agent.prompt.built_in_tools`): `transfer_to_number`, `transfer_to_agent`, `language_detection`, `voicemail_detection`, `play_keypad_touch_tone`
- API-created agents only get the built-ins listed in `agent-config.json`

## Prompt Conventions
- The first message is static and sent separately. Write the prompt as if it has already been said, never repeat it.
- First message usually includes agent name, business name, recording notice and an opener question.
- Never put call length limits in the prompt. `conversation.max_duration_seconds` handles it.
- Keep replies short and spoken. No markdown, lists or URLs read out loud.
- With `text_normalisation_type: system_prompt`, tell the agent to write numbers, prices and emails the way they should be spoken.

## Default Agent Settings
Source of truth: `templates/elevenlabs/agent-config.json`, used by `scripts/el.py create-agent`.

| Setting | Default | Notes |
|---------|---------|-------|
| LLM | `claude-haiku-4-5`, temp `0.3`, max_tokens `200` | Backups: gpt-4.1, gemini-2.5-flash, gpt-4.1-mini |
| TTS model | `eleven_v4_turbo` | ~100ms, current recommended. `eleven_flash_v2_5` is fastest (~75ms). `eleven_v3_conversational` for expressive/audio tags |
| Voice | stability `0.5`, similarity `0.8`, speed `1.0` | |
| Turn | `turn_v3`, eagerness `normal`, timeout `7s`, silence end `20s` | eagerness: patient / normal / eager |
| ASR | `scribe_realtime`, high quality | |
| Max duration | `240s` | Demo limit |

Deprecated: `optimize_streaming_latency` (no-op), `eleven_turbo_v2_5` (use flash v2.5), `prompt.tools` (use `tool_ids` / `built_in_tools`), the simulate-conversation endpoint (removed 31 Oct 2026, use agent testing).

## Knowledge Base / RAG
- Under ~1500 words: embed in the system prompt.
- Over that: `python3 scripts/el.py kb-add --text-file ... --agent-id ...` creates the doc, computes the RAG index and attaches it. No UI step needed anymore.
- RAG defaults: `e5_mistral_7b_instruct` (use `multilingual_e5_large_instruct` for non-English), max_vector_distance `0.4`, max_documents_length `500`, chunks `4`.

## Shareable Demo Link
```
https://elevenlabs.io/app/talk-to?agent_id={agent_id}
```
