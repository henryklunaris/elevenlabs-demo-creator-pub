---
name: vps-setup
description: Securely set up a fresh Ubuntu VPS for running Claude Code 24/7, driven from Claude Code on your laptop over SSH. Creates an SSH key, a non-root user with sudo, key-only logins, no root login, installs Claude Code for the new user with .env deny rules, and moves any existing projects. Use when the user says /vps-setup, wants to set up or lock down a VPS for Claude Code, or gives you a new server IP to configure.
---

# VPS setup for Claude Code

You are running on the user's laptop and setting up a remote Ubuntu server over SSH. Work step by step, check each result, and stop to ask when a step needs the user.

## Ground rules
- You cannot type passwords. Run every SSH command with `-o BatchMode=yes` so it fails fast instead of hanging.
- Never put secrets (passwords, API keys, tokens) in commands, chat or files. The user types those themselves in their own terminal.
- Keep a working root connection until the new user's login is tested. Never turn off root login first.
- Never use `pkill -f` with a pattern that also appears in your own SSH command, it kills your own session. Use `pkill -u root -x claude` instead.
- Never run `do-release-upgrade`.
- Before each step, say in one line what you're about to do.

## Inputs
Ask for anything missing:
- Server IP (from hPanel)
- Username to create (default: the user's first name, lowercase)
- Whether the SSH key was already added during server setup

## Step 1: SSH key and shortcuts (laptop)
0. If `~/.ssh/config` already has `Host vps` / `Host vps-root` entries, edit them in place to match the block in point 3 (including `IdentityFile ~/.ssh/vps`), don't add duplicates. If the IP changed after a reinstall, run `ssh-keygen -R <IP>` so the new server's fingerprint is accepted.
1. Never create the key yourself and never read the private key file. If `~/.ssh/vps.pub` doesn't exist, ask the user to run these in their own terminal. The first asks for a passphrase (they should set one), the second stores it in the macOS Keychain so `ssh` works without typing it:
```
ssh-keygen -t ed25519 -f ~/.ssh/vps -C "vps"
ssh-add --apple-use-keychain ~/.ssh/vps
```
   Wait for them. You may read `~/.ssh/vps.pub` (the public half is safe to share).
2. If the server isn't bought yet, copy the public key with `pbcopy < ~/.ssh/vps.pub` (macOS) and tell the user to paste it into "Add SSH key" on the server setup screen, next to the root password. Wait for them.
3. Add to `~/.ssh/config` if missing, then `chmod 600 ~/.ssh/config`:
```
Host vps
  HostName <IP>
  User <username>
  IdentityFile ~/.ssh/vps
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes

Host vps-root
  HostName <IP>
  User root
  IdentityFile ~/.ssh/vps
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes
```
4. Test: `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new vps-root whoami`
   - If it fails with a passphrase or agent error, ask the user to run `ssh-add --apple-use-keychain ~/.ssh/vps` again
   - If it fails, the key isn't on the server. Ask the user to run this in their own terminal (it needs the root password once): `ssh-copy-id -i ~/.ssh/vps.pub vps-root`

## Step 2: Look before changing anything
Run as root and report back briefly:
```
cat /etc/os-release | head -2; getent passwd | awk -F: '$3>=1000 && $3<65000 {print $1}'; ls -la /root; ls /root/.local/bin 2>/dev/null; sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'; grep -H . /etc/ssh/sshd_config.d/*.conf; pgrep -a -u root claude
```
Note any existing projects in `/root` and any running root Claude sessions.

## Step 3: Updates and tools
```
apt-get update && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && apt-get install -y gh
```
This can take a few minutes. If it asks for a reboot, tell the user and continue, the reboot can happen at the end.

## Step 4: Create the user
```
id <u> >/dev/null 2>&1 || adduser --disabled-password --gecos '' <u>
usermod -aG sudo <u>
install -d -m 700 -o <u> -g <u> /home/<u>/.ssh
```
Write only the laptop's public key (contents of `~/.ssh/vps.pub`) to `/home/<u>/.ssh/authorized_keys`, owned by the user, mode 600. Then:
```
loginctl enable-linger <u>
echo 'set -g mouse on' > /home/<u>/.tmux.conf && chown <u>:<u> /home/<u>/.tmux.conf
```
Test: `ssh -o BatchMode=yes vps whoami` must print the username.

## Step 5: Move existing work off root (only if there is any)
1. Stop root's Claude: `export PATH=/root/.local/bin:$PATH; claude daemon stop --any; tmux kill-server; pkill -u root -x claude`
2. Move project folders from `/root` into `/home/<u>/projects` and run `chown -R <u>:<u> /home/<u>/projects`
3. Show the result with `ls -la`

## Step 6: Claude Code for the user
As the user (`ssh vps`):
```
curl -fsSL https://claude.ai/install.sh | bash
grep -q '.local/bin' ~/.bashrc || echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
mkdir -p ~/.claude ~/projects
```
Write `~/.claude/settings.json` (merge if it exists, don't overwrite other keys):
```json
{
  "tui": "default",
  "permissions": {
    "deny": ["Read(**/.env)", "Read(**/.env.*)"]
  }
}
```
Confirm with `~/.local/bin/claude --version`.

## Step 7: sudo password (needs the user)
Ask the user to run these in their own terminal and tell you when `root` is printed:
```
ssh -t vps-root passwd <u>
ssh -t vps sudo whoami
```
Do not continue until they confirm. Without this they lose admin access in the next step.

## Step 8: Lock SSH
The `00-` prefix matters, because Ubuntu's `50-cloud-init.conf` may turn passwords back on and the first value wins.

On Hostinger, also keep the hPanel Browser terminal working. It logs in as root over SSH from `169.254.0.1`, an internal address that can't be reached from the internet, so allowing root from only that address is safe. On other providers, skip this file and check their console's address in `journalctl -u ssh` first.
```
printf "PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin no\n" > /etc/ssh/sshd_config.d/00-lockdown.conf
printf "Match Address 169.254.0.1\n  PermitRootLogin yes\n  PasswordAuthentication yes\n" > /etc/ssh/sshd_config.d/99-hostinger-console.conf
sshd -t && systemctl restart ssh
sshd -T | grep -E '^(passwordauthentication|permitrootlogin)'
sshd -T -C user=root,addr=169.254.0.1,host=x | grep -i permitrootlogin
```
The last line must print `permitrootlogin yes`.

Verify all three:
- `ssh -o BatchMode=yes vps whoami` works
- `ssh -o BatchMode=yes vps-root whoami` is rejected
- `ssh -o BatchMode=yes -o PubkeyAuthentication=no -o PreferredAuthentications=password vps` is rejected

If the user login fails, undo right away over the still-open root path, before anything else: `rm /etc/ssh/sshd_config.d/00-lockdown.conf && systemctl restart ssh`

Ask the user to click the Browser terminal button in hPanel and confirm it still opens. Remind them the dashboard's reset password and reinstall options are the emergency way back in.

## Step 9: Hand over
Tell the user to do these themselves (they need browser codes or secrets):
1. `ssh vps`, then `cd ~/projects && claude`, then `/login` with their Claude subscription (Remote Control doesn't work with API keys)
2. GitHub, in a plain terminal, not inside Claude:
   - Token: create a fine-grained PAT limited to the repos they need, then `gh auth login --with-token`, paste, Enter, Ctrl+D
   - Or browser: `gh auth login --web --git-protocol https`
   - Then `gh auth setup-git`
3. `.env` files: `nano ~/projects/<repo>/.env`, paste, save, `chmod 600 .env`. Never paste keys into Claude.
4. `claude agents`, start a session, `/rc`, then check it shows in the Claude app under Code
5. On the laptop, add `"Read(~/.ssh/**)"` to `permissions.deny` in `~/.claude/settings.json`. Claude can still log in through `ssh vps`, but can never open the key files. Done last because it also blocks the config edits above.
6. Optional: in the hosting dashboard, add a firewall that only accepts SSH (port 22), from their fixed VPN IP if they have one

Finish with a short summary of what changed and what was verified.
