# DeepMind Formal Conjectures handoff — restricted K6,D=3

Date: 2026-09-21
Public showcase copy: author and private contact metadata omitted.

## Current upstream status checked

Upstream file:
`google-deepmind/formal-conjectures/FormalConjectures/Paper/MonochromaticQuantumGraph.lean`

Observed current statuses:
- `eqSystem6_no_solution_d3`: research solved; external Lean 4 proof linked to algal/krenn-gu-6x3-certificate.
- `eqSystem6_no_solution_d4`: research solved.
- `eqSystem6_no_solution_d5`: research solved.
- `eqSystem6_no_solution_d6`: research solved.
- `eqSystem6_no_solution_ge3`: research open.

The upstream unrestricted D=3 theorem is strictly stronger than the restricted fixed-endpoint-colour simple-graph theorem in our manuscript.

## Restricted result to formalize independently

Model: simple K6, exactly one primitive edge per unordered vertex pair, one fixed ordered endpoint-colour pair per primitive edge, complex edge weights.

Target theorem: no restricted assignment satisfies monochromatic amplitudes 1 for all three colours and mixed amplitudes 0.

The intended Lean proof should validate the structural route itself, rather than merely deriving the restricted result from the already-solved unrestricted theorem.

## Exact verifier rerun on 2026-09-21

Two local verifier reruns completed successfully:

1. Symbolic equality / UNSAT-core verifier:
   PASS: 23/23 support-orbit representatives have an exact UNSAT core of size <= 3.

2. Direct inherited-colouring-bucket enumeration:
   PASS: all 23 support-orbit representatives are UNSAT.
   Total semantic endpoint-colour assignments checked: 1,217,855.

## Upstream Lean verification attempt

A GitHub Actions workflow was created in this private repository to clone the pinned public unrestricted Lean certificate and run `scripts/verify_release.sh`.

Runs:
- 35558519393 — failed before proof verification completed.
- 35558559543 — failed before proof verification completed.

Therefore these runs are NOT counted as an independent successful Lean rerun. The public certificate repository's own verification record remains upstream evidence only.

## Upstream contribution plan

Following CONTRIBUTING.md:
1. sign/check Google CLA;
2. open a dedicated issue for the solved restricted variant;
3. host the long independent Lean proof externally;
4. add a concise solved statement in FormalConjectures/Paper/MonochromaticQuantumGraph.lean;
5. attach `formal_proof using lean4` to the external pinned proof;
6. run `lake build`;
7. submit a PR.

A direct attempt to comment on upstream issue #4609 using the currently connected GitHub integration was rejected with HTTP 403 (resource not accessible by integration), so no upstream write has been claimed.
