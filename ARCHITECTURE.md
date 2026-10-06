# V.I.R.A.L.™ Motorsport Architecture

## Objective

V.I.R.A.L. is a public reference architecture for continuous vehicle-engineering reasoning.

Its job is not to reproduce a production race-engineering stack. Its job is to demonstrate a system capable of moving from **live operating relationships to evidence-backed engineering judgment** while preserving uncertainty, authority boundaries and outcome verification.

## Core reasoning contract

Every reasoning cycle answers:

1. What is happening?
2. Why might it be happening?
3. Which explanation best fits all available evidence?
4. What will probably happen next?
5. How certain am I?
6. What engineering response could preserve the vehicle?

Those answers are produced before the authority layer is consulted.

## Canonical signal relationship

The public data model is deliberately organized around engineering roles rather than vendor-specific channel names:

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

The architecture can therefore represent a condition in which achieved state still looks acceptable while the effort required to maintain it is increasing. That is a useful precursor because performance loss does not need to be visible before non-conformance can be detected.

## Module flow

### `SyntheticExpectedStateModel`
Produces an intentionally simplified contextual expectation for selected request, actuator, achieved-state, fuel-support and thermal channels.

The public model is deliberately transparent. It is not vehicle-specific calibration and is not presented as a production model.

### `StateInterpreter`
Computes relationship residuals and rates of change, including:

- requested-versus-achieved air-charge error
- actuator/control-effort residual
- mixture tracking error
- fuel-pressure tracking error
- thermal residuals
- correction activity
- hard-limit status
- synthetic composite engineering margin

The key distinction is that **non-conformance can exist while every individual channel is still inside a conventional limit**.

### `EvidenceAssembler`
Converts interpreted state into explicit evidence records.

Evidence can support or conflict with an engineering hypothesis. Conformant channels are not ignored; they can actively weaken an explanation. This is important because the system must be able to abandon an attractive but poorly supported diagnosis.

### `AdaptiveReasoningEngine`
Maintains belief across competing engineering explanations:

- developing thermal-management limitation
- air-charge / performance-control deviation
- fuel-delivery support deviation
- sensor or signal-integrity issue
- contextual transient

The public implementation uses transparent probabilistic evidence fusion and stateful belief smoothing. It is intentionally inspectable and reproducible.

Its purpose is to demonstrate **competing hypotheses + supporting evidence + conflicting evidence + revision**, not to disclose proprietary diagnostic intelligence.

### `MarginForecaster`
Projects synthetic engineering margin forward using the recent trend.

The forecaster can request preservation before a hard threshold is crossed when the current relationship indicates that available margin is narrowing rapidly.

### `AuthorityGate`
Deterministic control boundary around the probabilistic reasoner.

| Level | Public meaning |
|---|---|
| A0 | Observe |
| A1 | Advise |
| A2 | Request action |
| A3 | Simulate approved preservation action |

A3 in this repository never controls a real vehicle.

### `PreservationController`
Applies only a synthetic demand reduction to the simulator.

It contains no production commands, ECU-write implementation, ignition strategy, boost control table or manufacturer-specific control mechanism.

### `OutcomeVerifier`
Measures the post-action state and decides whether synthetic engineering margin is recovering, worsening or inconclusive.

This closes the loop. The system does not assume an action worked merely because it was issued.

### `HashChainedLedger`
Records the decision path in an append-only SHA-256 hash chain.

Each record contains its predecessor hash. Tests verify that payload tampering invalidates the chain.

## Why probabilistic reasoning is separated from authority

The reasoner may be wrong.

That is a design assumption, not an exception.

Therefore model output does not become engineering truth merely because a model produced it. The system keeps:

- inference probabilistic
- evidence explicit
- conflicting evidence visible
- confidence visible
- abstention available
- authority deterministic
- actions bounded
- outcomes verified

This separation is the core engineering-control pattern demonstrated by the repository.

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

The public architecture is designed so that stronger domain models can replace the synthetic components without changing the overall evidence, reasoning, authority and verification contracts.
