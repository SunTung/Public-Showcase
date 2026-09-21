# Lean formalization bring-up

This directory contains the first executable Lean kernel-check target for the
restricted K6/D=3 project.  It is deliberately a **bring-up theorem**, not a
claim that the full 23-orbit restricted impossibility has already been
formalized.  The full finite model still requires encoding the endpoint-colour
fibres and the 23 support-orbit certificate.

The target is useful because it verifies the toolchain, records the exact
scope boundary, and provides a clean place for the next theorem.

Run with Lean 4.  `lake build` must complete without `sorry`.
