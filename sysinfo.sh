#!/usr/bin/env bash
# Prints where this session is running. Read-only; the only network call is one local metadata probe.
set -u
echo "== hostname ==";      hostname
echo "== user ==";          id -un
echo "== cpu ==";           nproc
echo "== memory ==";        free -h | sed -n '1,2p'
echo "== os ==";            . /etc/os-release && echo "$PRETTY_NAME"
echo "== claude ==";        claude --version 2>/dev/null || echo "claude not on PATH"
echo "== git ==";           git --version
echo "== docker ==";        docker --version 2>/dev/null || echo "docker not available"
echo "== workdir ==";       pwd
echo "== session env ==";   env | grep -E '^CLAUDE_CODE_REMOTE' | sed 's/=.*/=<set>/' || true
echo "== EC2 metadata (should be BLOCKED on a hardened runner) =="
# -f makes curl fail on HTTP errors (e.g. 403 from a proxy), so only a real token counts as "reachable".
if TOKEN=$(curl -sf -m 2 --request PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" 2>/dev/null) && [ -n "$TOKEN" ]; then
  echo "REACHABLE: metadata endpoint returned a token (hop limit too high, or not inside a container)"
else
  echo "blocked or not on EC2 (good)"
fi
