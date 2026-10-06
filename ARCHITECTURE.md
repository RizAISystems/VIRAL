# V.I.R.A.L.™ Motorsport Architecture

## Objective

V.I.R.A.L. is a public reference architecture for **continuous vehicle engineering intelligence**.

Its purpose is not to recreate a production race-engineering stack. It demonstrates how a system can move from live operating relationships to evidence-backed engineering judgment across the vehicle lifecycle:

```text
OBSERVE → UNDERSTAND → PREDICT → PRESERVE → MAINTAIN → IMPROVE → DESIGN → VALIDATE → LEARN
```

The public implementation is intentionally synthetic and inspectable. It proves the architecture and the engineering contracts without publishing production vehicle models, calibration logic or proprietary engineering intelligence.

## Core reasoning contract

Every reasoning cycle answers:

1. What is happening?
2. Why might it be happening?
3. Which explanation best fits all available evidence?
4. What will probably happen next?
5. How certain am I?
6. What engineering response could preserve or improve the vehicle?

Those answers are produced before the authority layer is consulted.

## Canonical vehicle relationship

The public data model is organized around engineering roles rather than vendor-specific channel names:

```text
REQUEST / INTENT
    ↓
ACTUATOR EFFORT
    ↓
ACHIEVED STATE
    ↓
CORRECTIONS / COMPENSATIONS
    ↓
THERMAL + MECHANICAL RESPONSE
    ↓
OPERATING OUTCOME
```

This lets the architecture represent a condition in which achieved state still looks acceptable while the effort required to maintain it is increasing. Performance loss does not need to be visible before non-conformance can be detected.

## Runtime reasoning path

### `SyntheticExpectedStateModel`

Produces an intentionally simplified contextual expectation for request, actuator, achieved-state, fuel-support and thermal channels. It is not a vehicle-specific calibration model.

### `StateInterpreter`

Computes relationship residuals and rates of change, including requested-versus-achieved air-charge error, actuator-effort residual, mixture tracking error, fuel-pressure tracking error, thermal residuals, correction activity and composite engineering margin.

The important distinction is that **non-conformance can exist while every individual channel remains inside a conventional limit**.

### `EvidenceAssembler`

Turns interpreted state into explicit supporting and conflicting evidence. Conformant channels can actively weaken a hypothesis rather than being ignored.

### `AdaptiveReasoningEngine`

Maintains competing engineering explanations and revises belief as new evidence arrives. The public implementation uses transparent probabilistic evidence fusion and stateful smoothing so the reasoning path is auditable.

### `MarginForecaster`

Projects synthetic engineering margin forward from recent behavior and can identify a preservation need before a hard-limit event occurs.

### `AuthorityGate`

Separates probabilistic inference from deterministic permission.

| Level | Public meaning |
|---|---|
| A0 | Observe |
| A1 | Advise |
| A2 | Request action |
| A3 | Simulate approved preservation action |

A3 never controls a real vehicle.

### `PreservationController`

Applies only a synthetic demand reduction. It contains no production ECU command, calibration table or manufacturer-specific control method.

### `OutcomeVerifier`

Measures the post-action state and determines whether the vehicle is recovering, worsening or inconclusive. An issued action is never assumed to have worked.

## Engineering lifecycle layer

### `EngineeringReviewPlanner`

Extends the live reasoning result into post-event engineering work.

It converts the same evidence into four additional outputs:

1. **Condition-based maintenance** — sustained relationship drift becomes an inspection recommendation based on observed condition rather than mileage or a fault code.
2. **Ranked engineering responses** — multiple improvement paths are scored against the observed limitation and their modeled tradeoffs are kept visible.
3. **Design requirement generation** — when no synthetic catalog candidate satisfies the required constraints, the architecture produces a measurable engineering brief instead of force-fitting an available part.
4. **Modification validation** — a second synthetic run repeats comparable conditions after an engineering revision and measures whether the original limitation improved or moved elsewhere.

### Synthetic engineering-option ranking

The public option scores are deliberately simple. They are derived from the relative severity of control-effort, tracking and thermal evidence.

The purpose is to demonstrate the decision contract:

```text
observed limitation
    ↓
engineering objective
    ↓
candidate responses
    ↓
benefit + tradeoff comparison
    ↓
ranked recommendation
```

Production solution-ranking logic is deliberately absent.

### Design requirement generation

The public demonstration includes a small synthetic candidate set. If no candidate meets all stated thermal, pressure-drop, mass and packaging constraints, the planner generates a requirement for a purpose-designed solution.

This demonstrates a critical boundary between **selecting an existing part** and **defining the engineering problem that a new part must solve**.

### Comparable-condition validation

The flagship demo reruns the same synthetic duty cycle with an engineering revision. Validation compares:

- peak actuator-effort deviation
- peak requested-versus-achieved tracking error
- minimum engineering margin
- whether another subsystem becomes the stronger bottleneck

A modification is not treated as successful merely because a component changed. The result must be measured against the original limitation.

## Evidence ledger

`HashChainedLedger` records reasoning, authority, action, verification and engineering-review output in an append-only SHA-256 chain.

Tests verify that payload tampering invalidates the chain.

## Why probabilistic reasoning is separated from authority

The reasoner may be wrong. That is a design assumption, not an exception.

Therefore model output does not become engineering truth merely because a model produced it. The architecture keeps:

- inference probabilistic
- evidence explicit
- conflicting evidence visible
- confidence visible
- abstention available
- authority deterministic
- actions bounded
- outcomes verified
- engineering changes re-tested

## Portability

The architecture is deliberately vendor-neutral. The same contracts can support elite motorsport, OEM development, specialist performance engineering, club racing or lower-authority enthusiast applications.

What changes between deployments is the data fidelity, domain models, engineering history, authority and integration depth, not the fundamental reasoning loop.

## Public implementation boundary

The following are intentionally absent:

- real vehicle calibration models
- production decision thresholds
- manufacturer CAN mappings
- ECU write paths
- production control laws
- proprietary solution-ranking logic
- private engineering history
- persistent vehicle-specific learning
- proprietary failure signatures
- real component-selection databases
- private design optimization models

The public architecture is designed so stronger domain models can replace the synthetic components without changing the evidence, reasoning, authority, engineering-review and validation contracts.