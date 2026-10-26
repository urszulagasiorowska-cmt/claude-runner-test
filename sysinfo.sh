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
if curl -s -m 2 --request PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" >/dev/null 2>&1; then
  echo "REACHABLE: metadata endpoint answered (hop limit too high, or not inside a container)"
else
  echo "blocked or not on EC2 (good)"
fi
