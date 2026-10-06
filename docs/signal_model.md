# Public Signal Model

V.I.R.A.L. does not organize the demonstrator around one manufacturer's channel names. The public model uses generic engineering roles so the architecture remains portable.

| Role | Public synthetic examples | Why it matters |
|---|---|---|
| Request / intent | driver demand, torque request, air-charge target | What the vehicle is being asked to produce |
| Actuator effort | throttle, synthetic control command | How hard the control system is working to achieve the request |
| Achieved state | load, achieved air-charge state | What the vehicle actually produces |
| Corrections / compensations | mixture tracking, ignition correction | What the system is doing to remain inside the operating relationship |
| Support systems | fuel-pressure request vs achieved | Whether supporting subsystems remain conformant |
| Thermal response | coolant, oil, intake temperature | Resulting operating state |
| Context | speed, RPM, gear, ambient, grade, lateral load | Conditions under which the relationship must be interpreted |

## The key precursor

A conventional inspection of achieved output may still say the vehicle is performing normally.

V.I.R.A.L. separately observes whether **the amount of control effort required to maintain that output is changing**.

In the flagship scenario, actuator effort rises before requested-versus-achieved air-charge error becomes materially abnormal. Tests preserve that ordering.

This is the core architectural point: the system reasons over **relationships and trajectories**, not only absolute values.

## From signals to engineering decisions

The same canonical model also supports the downstream lifecycle:

```text
relationship drift
    ↓
condition evidence
    ↓
maintenance need
    ↓
engineering objective
    ↓
candidate change
    ↓
tradeoff / constraint evaluation
    ↓
validation under comparable conditions
```

That means a signal is not useful only because it can trigger an alert. It can also contribute to an engineering explanation, a maintenance recommendation, an upgrade decision or a design requirement.

All channels, values, thresholds, candidates and constraints in the repository are synthetic. No private calibration or production telemetry is included.