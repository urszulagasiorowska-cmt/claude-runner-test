#!/usr/bin/env bash
# Checks what a cloud environment's setup script installed and what the session's network can reach.
# Read-only. Network calls: one HEAD to Datadog, one to a private Twins ALB (expected to time out outside the VPC).
set -u
echo "== java ==";    java -version 2>&1 | grep -i 'version' | head -1 || echo "java not installed"
echo "== gradle =="; gradle --version 2>/dev/null | grep -E '^Gradle' || echo "gradle not installed"
echo "== node ==";   node --version 2>/dev/null || echo "node not installed"
echo "== docker =="; docker --version 2>/dev/null || echo "docker not available"
# probe <url>: prints the HTTP status the session actually got. 000 = no connection at all.
# A 403 from the session's outbound proxy means "blocked by allowlist"; any 2xx/4xx from the real host means "reachable".
probe() { curl -s -o /dev/null -m 5 -w '%{http_code}' "$1" 2>/dev/null || echo 000; }
echo "== network: Datadog (public SaaS, needs allowlist in option 2) =="
code=$(probe https://api.datadoghq.com/); echo "status $code -> $( [ "$code" = 000 ] || [ "$code" = 403 ] && echo blocked || echo reachable )"
echo "== network: private Twins ALB (inside VPC, expected: blocked unless self-hosted) =="
code=$(probe http://internal-priv-notification-alb-253185813.us-east-1.elb.amazonaws.com/); echo "status $code -> $( [ "$code" = 000 ] || [ "$code" = 403 ] && echo blocked || echo reachable )"
echo "== where am I ==";  hostname; nproc; free -h | sed -n 2p
