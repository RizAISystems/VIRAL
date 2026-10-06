# Public Signal Model

V.I.R.A.L. does not organize the demonstration around one manufacturer's channel names. The public model uses generic engineering roles so the architecture remains portable.

| Role | Public synthetic examples | Why it matters |
|---|---|---|
| Request / intent | driver demand, torque request, boost target | What the system is being asked to produce |
| Actuator effort | throttle, synthetic wastegate/control command | How hard the control system is working to achieve the request |
| Achieved state | load, achieved boost | What the vehicle actually produces |
| Corrections / compensations | mixture tracking, ignition correction | What the system is doing to remain inside the operating relationship |
| Support systems | fuel-pressure request vs achieved | Whether a supporting subsystem is conformant |
| Thermal response | coolant, oil, intake temperature | Resulting operating state |
| Context | speed, RPM, gear, ambient, grade, lateral load | Conditions under which the relationship must be interpreted |

## The key precursor

A conventional inspection of achieved output may say that the vehicle is still performing normally.

V.I.R.A.L. can separately observe that **the amount of control effort required to maintain that output is changing**.

In the flagship synthetic scenario, actuator effort begins to rise before requested-versus-achieved air-charge error becomes materially abnormal. The tests preserve that ordering.

This is the public architectural point: the system reasons over *relationships and trajectories*, not only absolute values.

All channels, values and thresholds in the repository are synthetic. No private calibration or production telemetry is included.
