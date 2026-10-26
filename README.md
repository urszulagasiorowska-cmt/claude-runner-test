# claude-runner-test

Tiny public repository used to verify a Claude Code **self-hosted environment** (TWINS-1552 PoC).

It has no application code. Its only purpose is to let a cloud session started at claude.ai/code run on our own runner and report where it executed.

- `sysinfo.sh` prints hostname, CPU, memory, OS, available tools and whether the EC2 metadata endpoint is reachable.
- Expected result on Anthropic's VM: hostname `vm`, Ubuntu 24.04, 4 CPU, ~15 GiB.
- Expected result on our runner: our container name, Debian from our image, our instance size, metadata endpoint blocked.
