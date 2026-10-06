# Public Scope and Deliberate Omissions

V.I.R.A.L.™ is a public engineering demonstrator, not a production vehicle-control system.

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
- accumulated engineering history
- vehicle-specific learning architecture
- production solution-ranking algorithms
- private failure or degradation signatures

## Design intent

The signal taxonomy is informed by the structure of real performance-vehicle logging, but every public value, coefficient, threshold, weighting and scenario transition is synthetic.

The public code should be sufficient for a technical reviewer to understand the engineering architecture and evaluate the implementation quality.

It should not be sufficient to recreate any undisclosed proprietary vehicle-intelligence product.
