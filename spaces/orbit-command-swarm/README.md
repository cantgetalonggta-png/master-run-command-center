---
title: Orbit Command Swarm Demo
emoji: 🛰️
colorFrom: green
colorTo: gray
sdk: static
pinned: false
license: mit
short_description: 23-agent MRCC swarm status demo (static)
---

# Orbit Command · Swarm Demo

Static Space demo for the **master-run-command-center** 23-agent swarm.

- Primary session lock: `211e2cba-1b23-5ce8-945a-d5e158b037a2`
- Agents: DEP / FE / RS / LC teams
- Live surfaces + local worker execution model

This Space does **not** host private models. It is a public status board for the swarm bridge.

## Deploy

```bash
hf auth login
hf spaces create <username>/orbit-command-swarm --sdk static
cd this-folder && hf spaces upload <username>/orbit-command-swarm .
```
