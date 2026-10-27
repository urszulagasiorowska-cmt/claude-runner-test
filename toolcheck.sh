#!/usr/bin/env bash
# Checks what a cloud environment's setup script installed and what the session's network can reach.
# Read-only. Network calls: one HEAD to Datadog, one to a private Twins ALB (expected to time out outside the VPC).
set -u
echo "== java ==";    java -version 2>&1 | head -1 || echo "java not installed"
echo "== gradle =="; gradle --version 2>/dev/null | grep -E '^Gradle' || echo "gradle not installed"
echo "== node ==";   node --version 2>/dev/null || echo "node not installed"
echo "== docker =="; docker --version 2>/dev/null || echo "docker not available"
echo "== network: Datadog (public SaaS, needs allowlist in option 2) =="
if curl -sI -m 5 https://api.datadoghq.com >/dev/null 2>&1; then echo "reachable"; else echo "blocked"; fi
echo "== network: private Twins ALB (inside VPC, expected: blocked unless self-hosted) =="
if curl -s -m 5 http://internal-priv-notification-alb-253185813.us-east-1.elb.amazonaws.com/ >/dev/null 2>&1; then echo "reachable"; else echo "blocked (expected outside VPC)"; fi
echo "== where am I ==";  hostname; nproc; free -h | sed -n 2p
