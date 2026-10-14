#!/usr/bin/env python3
"""ElevenLabs Agents CLI. Replaces the ElevenLabs MCP with direct API calls (stdlib only).

Run `python3 scripts/el.py -h` or `python3 scripts/el.py <command> -h` for usage.
"""

import argparse, json, mimetypes, os, sys, time, urllib.error, urllib.parse, urllib.request, uuid

API = "https://api.elevenlabs.io"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CONFIG_PATH = os.path.join(ROOT, "templates", "elevenlabs", "agent-config.json")


def get_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    env_path = os.path.join(ROOT, ".env")
    if not key and os.path.exists(env_path):
        for line in open(env_path):
            if line.strip().startswith("ELEVENLABS_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("Error: ELEVENLABS_API_KEY not set in .env or environment")
    return key


def request(method, path, body=None, params=None, files=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
    headers = {"xi-api-key": get_api_key()}
    data = None
    if files is not None:
        data, headers["Content-Type"] = encode_multipart(body or {}, files)
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw, strict=False) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code} on {method} {path}: {e.read().decode(errors='replace')}")


def encode_multipart(fields, files):
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, path in files.items():
        mime = mimetypes.guess_type(path)[0] or "text/plain"
        head = f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{os.path.basename(path)}"\r\nContent-Type: {mime}\r\n\r\n'
        parts.append(head.encode() + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def out(data):
    print(json.dumps(data, indent=2))


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def deep_merge(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def config_overrides(a):
    """Build a partial conversation_config from CLI flags."""
    cc = {"agent": {"prompt": {}}, "tts": {}, "conversation": {}}
    if getattr(a, "prompt_file", None):
        cc["agent"]["prompt"]["prompt"] = read_text(a.prompt_file).strip()
    if getattr(a, "first_message", None):
        cc["agent"]["first_message"] = a.first_message
    if getattr(a, "language", None):
        cc["agent"]["language"] = a.language
    if getattr(a, "llm", None):
        cc["agent"]["prompt"]["llm"] = a.llm
    if getattr(a, "voice_id", None):
        cc["tts"]["voice_id"] = a.voice_id
    if getattr(a, "tts_model", None):
        cc["tts"]["model_id"] = a.tts_model
    if getattr(a, "max_duration", None):
        cc["conversation"]["max_duration_seconds"] = a.max_duration
    return {k: v for k, v in cc.items() if v and v != {"prompt": {}}}


def demo_url(agent_id):
    return f"https://elevenlabs.io/app/talk-to?agent_id={agent_id}"


# ---------- agents ----------

def cmd_create_agent(a):
    body = json.load(open(a.config or CONFIG_PATH))
    body.pop("_notes", None)
    deep_merge(body["conversation_config"], config_overrides(a))
    body["name"] = a.name
    res = request("POST", "/v1/convai/agents/create", body)
    agent_id = res["agent_id"]
    print(f"Created agent: {agent_id}\nDemo URL: {demo_url(agent_id)}")


def cmd_update_agent(a):
    body = {}
    cc = config_overrides(a)
    if cc:
        body["conversation_config"] = cc
    if a.name:
        body["name"] = a.name
    if a.json:
        deep_merge(body, json.load(open(a.json)))
    if not body:
        sys.exit("Nothing to update. Pass flags or --json.")
    res = request("PATCH", f"/v1/convai/agents/{a.agent_id}", body)
    print(f"Updated agent '{res.get('name')}' ({a.agent_id})")


def cmd_get_agent(a):
    res = request("GET", f"/v1/convai/agents/{a.agent_id}")
    if a.full:
        return out(res)
    cc = res["conversation_config"]
    p = cc["agent"]["prompt"]
    out({
        "agent_id": res["agent_id"],
        "name": res["name"],
        "llm": p.get("llm"),
        "tts_model": cc["tts"].get("model_id"),
        "voice_id": cc["tts"].get("voice_id"),
        "first_message": cc["agent"].get("first_message"),
        "knowledge_base": p.get("knowledge_base"),
        "rag_enabled": (p.get("rag") or {}).get("enabled"),
        "max_duration_seconds": cc.get("conversation", {}).get("max_duration_seconds"),
        "demo_url": demo_url(res["agent_id"]),
    })


def cmd_list_agents(a):
    res = request("GET", "/v1/convai/agents", params={"search": a.search, "page_size": a.limit})
    for ag in res.get("agents", []):
        print(f"{ag['agent_id']}  {ag['name']}")


# ---------- knowledge base ----------

def create_kb_doc(a):
    if a.url:
        return request("POST", "/v1/convai/knowledge-base/url", {"url": a.url, "name": a.name})
    if a.text_file:
        return request("POST", "/v1/convai/knowledge-base/text", {"text": read_text(a.text_file), "name": a.name})
    return request("POST", "/v1/convai/knowledge-base/file", {"name": a.name} if a.name else {}, files={"file": a.file})


def compute_rag_index(doc_id, model, timeout=120):
    print(f"Indexing {doc_id} for RAG...")
    start = time.time()
    while True:
        res = request("POST", f"/v1/convai/knowledge-base/{doc_id}/rag-index", {"model": model})
        status = res.get("status")
        if status == "succeeded":
            return
        if status in ("failed", "rag_limit_exceeded", "document_too_small", "cannot_index_folder"):
            sys.exit(f"RAG indexing failed: {res}")
        if time.time() - start > timeout:
            sys.exit(f"RAG indexing still '{status}' after {timeout}s. Re-run kb-attach later.")
        time.sleep(3)


def attach_kb(agent_id, doc_id, doc_name, doc_type, rag):
    agent = request("GET", f"/v1/convai/agents/{agent_id}")
    prompt = agent["conversation_config"]["agent"]["prompt"]
    kb = [d for d in prompt.get("knowledge_base", []) if d["id"] != doc_id]
    kb.append({"type": doc_type, "name": doc_name, "id": doc_id, "usage_mode": "auto"})
    # Minimal PATCH: sending the full conversation_config back has caused KB changes not to persist
    patch_prompt = {"knowledge_base": kb}
    if rag:
        cfg = json.load(open(CONFIG_PATH))["conversation_config"]["agent"]["prompt"]["rag"]
        patch_prompt["rag"] = dict(cfg, enabled=True)
        compute_rag_index(doc_id, cfg["embedding_model"])
    request("PATCH", f"/v1/convai/agents/{agent_id}", {"conversation_config": {"agent": {"prompt": patch_prompt}}})
    print(f"Attached '{doc_name}' ({doc_id}) to {agent_id}. RAG: {'on' if rag else 'off'}")


def cmd_kb_add(a):
    if not (a.url or a.text_file or a.file):
        sys.exit("Pass one of --url, --text-file, --file")
    doc = create_kb_doc(a)
    doc_type = "url" if a.url else "text" if a.text_file else "file"
    print(f"KB document created: {doc['id']} ({doc.get('name')})")
    if a.agent_id:
        attach_kb(a.agent_id, doc["id"], doc.get("name") or a.name, doc_type, not a.no_rag)


def cmd_kb_attach(a):
    doc = request("GET", f"/v1/convai/knowledge-base/{a.doc_id}")
    attach_kb(a.agent_id, a.doc_id, doc.get("name", a.doc_id), doc.get("type", "file"), not a.no_rag)


def cmd_kb_list(a):
    res = request("GET", "/v1/convai/knowledge-base", params={"search": a.search, "page_size": a.limit})
    for d in res.get("documents", []):
        print(f"{d['id']}  {d.get('type', ''):5}  {d.get('name')}")


# ---------- voices ----------

def cmd_voices(a):
    res = request("GET", "/v2/voices", params={"search": a.search, "page_size": a.limit, "voice_type": a.type})
    for v in res.get("voices", []):
        labels = ", ".join(f"{k}: {val}" for k, val in (v.get("labels") or {}).items())
        print(f"{v['voice_id']}  {v['name']}  [{labels}]")


def cmd_shared_voices(a):
    params = {"search": a.search, "page_size": a.limit, "gender": a.gender, "language": a.language, "accent": a.accent}
    res = request("GET", "/v1/shared-voices", params=params)
    for v in res.get("voices", []):
        print(f"{v['voice_id']}  {v['name']}  [{v.get('gender')}, {v.get('accent')}, {v.get('language')}]  public_owner_id={v.get('public_owner_id')}")


def cmd_add_voice(a):
    res = request("POST", f"/v1/voices/add/{a.public_owner_id}/{a.voice_id}", {"new_name": a.name})
    print(f"Added to your voices: {res.get('voice_id')}")


# ---------- calls ----------

def cmd_phones(a):
    for p in request("GET", "/v1/convai/phone-numbers"):
        agent = (p.get("assigned_agent") or {}).get("agent_name")
        print(f"{p['phone_number_id']}  {p['phone_number']}  {p.get('provider')}  agent={agent}")


def cmd_call(a):
    path = "/v1/convai/sip-trunk/outbound-call" if a.sip else "/v1/convai/twilio/outbound-call"
    body = {"agent_id": a.agent_id, "agent_phone_number_id": a.phone_number_id, "to_number": a.to}
    out(request("POST", path, body))


def main():
    p = argparse.ArgumentParser(description="ElevenLabs Agents CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    def agent_flags(s):
        s.add_argument("--prompt-file", help="System prompt file (md/txt)")
        s.add_argument("--first-message")
        s.add_argument("--voice-id")
        s.add_argument("--llm", help="e.g. gpt-4.1, gemini-2.5-flash, claude-haiku-4-5")
        s.add_argument("--tts-model", help="e.g. eleven_v4_turbo, eleven_flash_v2_5")
        s.add_argument("--language", help="e.g. en, de, fr")
        s.add_argument("--max-duration", type=int, help="Max call length in seconds")

    s = sub.add_parser("create-agent", help="Create agent from templates/elevenlabs/agent-config.json")
    s.add_argument("--name", required=True)
    s.add_argument("--config", help="Alternate base config JSON")
    agent_flags(s)
    s.set_defaults(fn=cmd_create_agent)

    s = sub.add_parser("update-agent", help="Patch an existing agent")
    s.add_argument("agent_id")
    s.add_argument("--name")
    s.add_argument("--json", help="JSON file deep-merged into the PATCH body")
    agent_flags(s)
    s.set_defaults(fn=cmd_update_agent)

    s = sub.add_parser("get-agent", help="Show agent summary")
    s.add_argument("agent_id")
    s.add_argument("--full", action="store_true", help="Print full raw config")
    s.set_defaults(fn=cmd_get_agent)

    s = sub.add_parser("list-agents")
    s.add_argument("--search")
    s.add_argument("--limit", type=int, default=30)
    s.set_defaults(fn=cmd_list_agents)

    s = sub.add_parser("kb-add", help="Create KB doc (and optionally attach + RAG index)")
    s.add_argument("--name")
    s.add_argument("--url")
    s.add_argument("--text-file")
    s.add_argument("--file", help="PDF, TXT, DOCX, HTML, EPUB, MD")
    s.add_argument("--agent-id", help="Attach to this agent after creating")
    s.add_argument("--no-rag", action="store_true", help="Attach without enabling RAG")
    s.set_defaults(fn=cmd_kb_add)

    s = sub.add_parser("kb-attach", help="Attach an existing KB doc to an agent")
    s.add_argument("agent_id")
    s.add_argument("doc_id")
    s.add_argument("--no-rag", action="store_true")
    s.set_defaults(fn=cmd_kb_attach)

    s = sub.add_parser("kb-list")
    s.add_argument("--search")
    s.add_argument("--limit", type=int, default=30)
    s.set_defaults(fn=cmd_kb_list)

    s = sub.add_parser("voices", help="Search voices in your account")
    s.add_argument("--search")
    s.add_argument("--type", help="personal, community, default, workspace, saved")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(fn=cmd_voices)

    s = sub.add_parser("shared-voices", help="Search the public voice library")
    s.add_argument("--search")
    s.add_argument("--gender")
    s.add_argument("--language", help="e.g. en, de")
    s.add_argument("--accent")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(fn=cmd_shared_voices)

    s = sub.add_parser("add-voice", help="Add a library voice to your account")
    s.add_argument("public_owner_id")
    s.add_argument("voice_id")
    s.add_argument("--name", required=True)
    s.set_defaults(fn=cmd_add_voice)

    s = sub.add_parser("phones", help="List phone numbers")
    s.set_defaults(fn=cmd_phones)

    s = sub.add_parser("call", help="Start an outbound call")
    s.add_argument("agent_id")
    s.add_argument("phone_number_id")
    s.add_argument("to", help="E.164 number, e.g. +447700900000")
    s.add_argument("--sip", action="store_true", help="Use SIP trunk instead of Twilio")
    s.set_defaults(fn=cmd_call)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
