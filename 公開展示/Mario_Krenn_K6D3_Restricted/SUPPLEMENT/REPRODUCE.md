# Reproducing the finite certificate

## Requirements

- Python 3.11 or newer is recommended.
- No third-party Python package is required by either verifier.

## Run the symbolic verifier

```bash
python3 k6d3_restricted_symbolic_certificate_verifier.py
```

Expected final line:

```text
PASS: restricted model: 23/23 support-orbit representatives have an exact UNSAT core of size <= 3.
```

The program reconstructs the 15 perfect matchings, 80 witness triples, 60/20 geometry split, witness-set stabilizers and all 23 support orbits. It then checks exact endpoint-colour equality constraints and finds a contradiction core of size at most three surviving perfect matchings for every support orbit.

## Run the direct verifier

```bash
python3 k6d3_restricted_direct_enumeration_verifier.py
```

Expected final lines:

```text
PASS: all 23 support-orbit representatives are UNSAT by direct IVC-bucket enumeration.
total semantic endpoint assignments checked = 1217855
```

The direct verifier does not use the symbolic equality/DSU contradiction method. It reconstructs the finite reduction and directly enumerates semantically distinct endpoint-colour assignments on present optional edges, computes surviving perfect matchings and inherited vertex-colouring bucket multiplicities, and searches for a candidate with no mixed singleton fiber.

## Release rerun recorded in this package

The 2026-09-21 rerun completed with exit code 0 for both programs. Measured wall times were approximately 0.66 seconds and 18.33 seconds, respectively, in the archival environment.

## Trust boundary

The theorem statement is a computer-assisted result for the restricted model described in the manuscript. The analytic witness lemmas and singleton-amplitude contradiction are proved in the manuscript. The universal finite singleton-forcing step is certified by exhaustive computation. The two programs use different contradiction machinery but share the same public mathematical model and reduction target.
