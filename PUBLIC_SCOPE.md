# Public Scope and Deliberate Omissions

V.I.R.A.L.™ Motorsport is a public engineering-intelligence demonstrator, not a production vehicle-control system.

## Included publicly

- synthetic request / intent signals
- synthetic actuator-effort signals
- synthetic achieved-state signals
- synthetic correction / compensation signals
- synthetic thermal and operating context
- contextual expected-state comparison
- requested-versus-achieved residuals
- control-effort residuals and rates of change
- supporting and conflicting evidence
- competing engineering hypotheses
- probabilistic belief revision
- confidence and abstention
- trend-based margin forecast
- A0–A3 authority states
- simulated bounded preservation
- post-action verification
- condition-based maintenance assessment
- ranked synthetic engineering responses
- synthetic component tradeoff evaluation
- design-requirement generation when no candidate meets constraints
- comparable-condition modification validation
- replacement-bottleneck check
- hash-chained decision logging
- deterministic tests and CI

## Deliberately withheld

The repository does not contain:

- real production telemetry
- private calibration files
- proprietary vehicle models
- manufacturer-specific decoding
- production engineering thresholds
- actual ECU control interfaces
- ignition, boost, torque or fuel-control strategy
- calibration tables or tuning logic
- proprietary diagnostic weighting
- private component-selection logic
- private supplier/component databases
- accumulated engineering history
- vehicle-specific learning architecture
- production solution-ranking algorithms
- private failure or degradation signatures
- production CAD/CAE or design-optimization logic

## Design intent

The signal taxonomy is informed by the structure of real performance-vehicle logging, but every public value, coefficient, threshold, weighting, candidate component and scenario transition is synthetic.

The code is intended to let a technical reviewer evaluate the architecture: relationship-based state interpretation, evidence fusion, uncertainty, authority separation, maintenance reasoning, engineering-option ranking, design-requirement generation and closed-loop validation.

It is intentionally not sufficient to recreate an undisclosed production vehicle-intelligence system.