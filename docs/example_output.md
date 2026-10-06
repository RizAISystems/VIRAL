# Example Decision Trace

Captured from `python demo.py` using the synthetic flagship scenario.

```text
V.I.R.A.L.™ Motorsport — Vehicle Intelligence Reference Architecture Lab™
Synthetic public reference demonstration. No production vehicle control logic is included.

T+000s
STATE        Vehicle state remains conformant with the public synthetic operating model.
BEST FIT     No abnormal engineering explanation is warranted by the current evidence.
CONFIDENCE   0.19
MARGIN       current=1.00 projected=1.00
RELATIONSHIP control_effort=+0.00% boost_error=0.022bar
FORECAST     No near-term synthetic operating constraint is projected from the current trend.
RESPONSE     No intervention justified; continue observation.
AUTHORITY    requested=A1 granted=A1
EVIDENCE     mixture_tracking_conformant, fuel_pressure_tracking_conformant
TOP BELIEF   transient_context=0.29
------------------------------------------------------------------------------------------------
T+025s
STATE        A developing non-conformance is present, but the vehicle remains inside the synthetic hard limits.
BEST FIT     Developing thermal-management limitation
CONFIDENCE   0.34
MARGIN       current=0.99 projected=1.00
RELATIONSHIP control_effort=+0.42% boost_error=0.022bar
FORECAST     No near-term synthetic operating constraint is projected from the current trend.
RESPONSE     No intervention justified; continue observation.
AUTHORITY    requested=A1 granted=A1
EVIDENCE     coolant_rate_shift, mixture_tracking_conformant, fuel_pressure_tracking_conformant
TOP BELIEF   thermal_management=0.39
------------------------------------------------------------------------------------------------
T+048s
STATE        A developing non-conformance is present, but the vehicle remains inside the synthetic hard limits.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.43
MARGIN       current=0.91 projected=0.83
RELATIONSHIP control_effort=+2.49% boost_error=0.022bar
FORECAST     No near-term synthetic operating constraint is projected from the current trend.
RESPONSE     No intervention justified; continue observation.
AUTHORITY    requested=A1 granted=A1
REVISION     Primary explanation revised from 'Developing thermal-management limitation' to 'Air-charge / performance-control deviation' as new evidence arrived.
EVIDENCE     control_effort_rate_shift, coolant_nonconformance, thermal_crosscheck_conflict, mixture_tracking_conformant, fuel_pressure_tracking_conformant
TOP BELIEF   air_charge_control=0.52
------------------------------------------------------------------------------------------------
T+088s
STATE        Live data is no longer fully conformant with expected operation and available engineering margin is narrowing.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.87
MARGIN       current=0.39 projected=0.00
RELATIONSHIP control_effort=+16.41% boost_error=0.230bar
FORECAST     If the current trend persists, the synthetic operating margin is projected to become critically narrow within the next ~20 seconds.
RESPONSE     Request a bounded preservation state and verify whether the vehicle returns toward its expected operating relationship.
AUTHORITY    requested=A3 granted=A3
EVIDENCE     control_effort_rate_shift, requested_achieved_divergence, boost_error_growth, intake_nonconformance, coolant_rate_shift
ACTION       bounded_preservation_state approved=True demand_reduction=8.0%
TOP BELIEF   air_charge_control=0.86
------------------------------------------------------------------------------------------------
T+092s
STATE        Live data is no longer fully conformant with expected operation and available engineering margin is narrowing.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.84
MARGIN       current=0.54 projected=0.34
RELATIONSHIP control_effort=+13.78% boost_error=0.195bar
FORECAST     The vehicle remains operational, but the current trend is reducing available synthetic engineering margin.
RESPONSE     Continue at current authority while monitoring for convergence, recovery or further margin loss.
AUTHORITY    requested=A1 granted=A1
EVIDENCE     requested_achieved_divergence, intake_nonconformance, mixture_tracking_conformant, fuel_pressure_tracking_conformant, correction_activity
TOP BELIEF   air_charge_control=0.86
------------------------------------------------------------------------------------------------
T+095s
STATE        A developing non-conformance is present, but the vehicle remains inside the synthetic hard limits.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.82
MARGIN       current=0.61 projected=1.00
RELATIONSHIP control_effort=+11.85% boost_error=0.169bar
FORECAST     No near-term synthetic operating constraint is projected from the current trend.
RESPONSE     No intervention justified; continue observation.
AUTHORITY    requested=A1 granted=A1
EVIDENCE     requested_achieved_divergence, intake_nonconformance, mixture_tracking_conformant, fuel_pressure_tracking_conformant, correction_activity
VERIFICATION stabilized: The synthetic vehicle state is recovering after the bounded preservation action.
TOP BELIEF   air_charge_control=0.86
------------------------------------------------------------------------------------------------
T+125s
STATE        A developing non-conformance is present, but the vehicle remains inside the synthetic hard limits.
BEST FIT     Air-charge / performance-control deviation
CONFIDENCE   0.73
MARGIN       current=0.83 projected=0.82
RELATIONSHIP control_effort=+5.42% boost_error=0.077bar
FORECAST     No near-term synthetic operating constraint is projected from the current trend.
RESPONSE     No intervention justified; continue observation.
AUTHORITY    requested=A1 granted=A1
EVIDENCE     requested_achieved_divergence, intake_nonconformance, mixture_tracking_conformant, fuel_pressure_tracking_conformant
TOP BELIEF   air_charge_control=0.83
------------------------------------------------------------------------------------------------
Ledger valid: True
Ledger path: artifacts/viral_ledger.jsonl
```
