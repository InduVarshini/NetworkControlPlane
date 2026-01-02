# AGENTS.md

## NetworkControlPlane

**Centralized Network Configuration, Automation, and Observability**

This document defines how AI coding agents (Cursor, Copilot, or similar) should assist in developing **NetworkControlPlane**.

The goal is to build a **networking-forward, production-style system** that clearly demonstrates **network control plane concepts, automation workflows, and observability**,

---

## Project Intent (Read First)

**NetworkControlPlane** is a **local network control plane and observability system** that simulates how modern production networks are:

* configured centrally
* automated via declarative intent
* monitored through real-time telemetry
* validated under failure and congestion scenarios

The project must read as **real network infrastructure work**, not coursework or experimentation.

---

## Target Audience

This project is optimized for:

* Network Infrastructure Engineering
* Systems / Infra SWE roles
* Recruiters skimming LinkedIn or GitHub in under 30 seconds

Clarity, terminology, and intent matter more than scale.

---

## Core Concepts This Project Must Convey

Agents should ensure the codebase clearly demonstrates:

### Control Plane Concepts

* declarative desired state (YAML)
* separation of intent, deployment, and observation
* centralized configuration logic

### Network Automation

* config generation via templates
* idempotent deployment
* device/session abstraction similar to Netmiko
* Ansible-style apply-desired-state workflow

### Network Observability

* live telemetry collection
* latency, packet loss, throughput
* interface counters
* routing/path visibility
* feedback loop between telemetry and validation

### Validation Under Realistic Scenarios

* baseline connectivity
* link failure
* congestion injection
* before/after comparison

---

## Required Terminology (Must Appear in Code & Docs)

Agents should consistently use the following language in:

* docstrings
* comments
* logs
* function names

Required terms:

* simulated network topology
* network control plane
* centralized configuration
* network automation
* desired state
* configuration rendering
* deployment abstraction
* Netmiko-style automation
* telemetry collection
* latency, packet loss, throughput
* interface counters
* routing / path validation
* failure scenarios
* congestion scenarios
* observability feedback loop

These terms are intentional and aligned with recruiter keyword searches.

---

## What This Project Is NOT

Agents must **not** turn this into:

* a full SDN controller
* a real hardware automation system
* a Kubernetes platform
* a cloud-native microservices system
* an ML or AIOps project
* a frontend-heavy application

Local simulation and simplified abstractions are **intentional and acceptable**.

---

## Architectural Contract

Agents must preserve the following architecture and separation of concerns:

```
YAML Desired State
        ↓
Configuration Rendering (Jinja2)
        ↓
Automation / Deployment Layer
        ↓
Simulated Network Topology
        ↓
Telemetry Collection
        ↓
Validation Logic
        ↓
Control Plane Interface (CLI / UI)
```

Each layer should:

* have a clear responsibility
* expose simple, explicit interfaces
* be explainable in an interview setting

---

## Automation Layer Expectations

The automation layer must:

* expose a **Netmiko-style lifecycle**

  * connect
  * send_config
  * commit
  * disconnect
* abstract device/session interactions
* be idempotent
* fail safely with clear logs

Implementation may be local (Mininet / namespace execution) but must **read like real network automation**.

Do **not** require real network devices or credentials.

---

## Telemetry Expectations

Telemetry must be:

* collected from real system signals (not mocked)
* sampled periodically
* lightweight and robust
* resilient to partial failures

Minimum required telemetry:

* ping-based latency and packet loss
* traceroute-based path visibility
* interface counters (bytes and drops)
* optional throughput testing via iperf3

Agents should prioritize:

* correct parsing
* clear units
* graceful error handling

---

## Validation Logic Expectations

Validation logic must:

* compare baseline vs post-change state
* detect meaningful behavioral changes
* produce structured pass/fail results
* be deterministic and repeatable

Validation should explicitly answer:

> "Did the network behave as expected under this scenario?"

Avoid probabilistic or ML-based approaches.

---

## Control Plane UI Expectations

The UI is a **control surface**, not a product.

Agents should:

* keep UI minimal
* prioritize visibility of telemetry and state
* provide explicit control actions

Acceptable UI features:

* topology status
* recent telemetry samples
* current routing/path
* validation results
* buttons for deploy, fail, restore, validate

Avoid:

* heavy JavaScript frameworks
* complex frontend state management
* visual polish over clarity

---

## Logging and Explainability

Logs should:

* describe actions in networking terms
* reflect control-plane intent
* be readable during a demo

Example log styles:

* "Applying desired network configuration to node s1"
* "Detected path change after link failure"
* "Latency exceeded baseline during congestion scenario"

Logs should help a human **explain the system verbally**.

---

## Coding Style Guidelines

Agents should:

* favor explicit, readable code
* avoid clever abstractions
* use descriptive names
* include docstrings that explain *network intent*, not just logic
* keep files small and focused

Readability > performance > extensibility.

---

## Performance & Stability

Agents must:

* avoid blocking the UI thread
* bound telemetry loops
* clean up Mininet state on shutdown
* handle missing tools gracefully

Correct behavior under demo conditions is more important than raw performance.

---

## Stretch Features (Out of Scope Unless Requested)

Do NOT implement unless explicitly asked:

* Prometheus exporters
* persistent time-series databases
* config diff visualizations
* SLO enforcement engines
* eBPF-based telemetry
* distributed deployments

The MVP is intentionally constrained.

---

## Definition of Success

An agent has succeeded if a user can:

1. Start a simulated network topology locally
2. Apply centralized configuration from YAML
3. Observe live network telemetry
4. Inject failures or congestion
5. Validate routing and connectivity behavior
6. Explain the system clearly using production networking language

---

## Final Note to Agents

This project is about **how clearly it maps to real network operations**.

If a design choice improves:

* recruiter comprehension
* interview explainability
* alignment with real-world network workflows

Prefer it — even if it sacrifices generality or sophistication.

