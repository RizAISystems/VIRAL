# Example Decision Trace

Representative output from `python demo.py` using the synthetic flagship scenario.

```text
T+048s
STATE        A developing non-conformance is present, but the vehicle remains inside the synthetic hard limits.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.43
MARGIN       current=0.91 projected=0.83
RELATIONSHIP control_effort=+2.49% tracking_error=0.022bar
REVISION     Primary explanation revised from 'Developing thermal-management limitation'
             to 'Air-charge / performance-control deviation' as new evidence arrived.

T+088s
STATE        Live data is no longer fully conformant with expected operation and available engineering margin is narrowing.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.87
MARGIN       current=0.39 projected=0.00
RELATIONSHIP control_effort=+16.41% tracking_error=0.230bar
FORECAST     If the current trend persists, the synthetic operating margin is projected to become critically narrow within the next ~20 seconds.
ACTION       bounded_preservation_state approved=True demand_reduction=8.0%

T+095s
VERIFICATION stabilized: The synthetic vehicle state is recovering after the bounded preservation action.

ENGINEERING LIFECYCLE REVIEW

CONDITION-BASED MAINTENANCE
SYSTEM       air-charge control path and thermal-support system
CONFIDENCE   0.87
RECOMMEND    Inspect the air-charge control path, sealing/flow path and thermal-support hardware before the next comparable sustained high-load session.

RANKED ENGINEERING RESPONSES
1. Flow-path efficiency redesign | score=0.920 | modeled_margin_gain=+19.0%
2. Charge-air heat-rejection upgrade | score=0.894 | modeled_margin_gain=+16.0%
3. Calibration-only preservation envelope | score=0.667 | modeled_margin_gain=+8.0%

DESIGN REQUIREMENT
TRIGGER      No synthetic catalog candidate simultaneously satisfies the required control-effort, tracking, thermal, pressure-drop, mass and packaging constraints.
TARGET       Peak control-effort reduction: >= 35% under the same synthetic duty cycle.
TARGET       Requested-versus-achieved tracking-error reduction: >= 20%.
TARGET       Thermal rejection / recovery capability: >= +18% versus the synthetic baseline.
TARGET       Additional pressure drop: <= 4%.
TARGET       Mass increase: <= 1.8 kg.
TARGET       Packaging-envelope growth: <= 6%.

MODIFICATION VALIDATION
STATUS       validated
CONTROL      baseline=15.73% revised=8.18%
TRACKING     baseline=0.141bar revised=0.093bar
MARGIN       baseline_min=0.58 revised_min=0.76
BOTTLENECK   moved=False
```

All values are synthetic. The public value is the evidence-to-engineering workflow and the fact that the implementation verifies those behaviors with deterministic tests.