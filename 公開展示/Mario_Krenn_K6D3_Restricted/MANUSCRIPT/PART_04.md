The contribution of the present result is therefore methodological and explanatory rather than a stronger parameter-range theorem. In the restricted model, the contradiction admits the compact chain

$$
\begin{aligned}
\text{monochromatic normalization} &\Rightarrow \text{nonzero witnesses}\\
&\Rightarrow \text{forced support}\\
&\Rightarrow \text{mixed singleton fiber}\\
&\Rightarrow A(c_{\mathrm{mixed}})\neq0. \qquad (18)
\end{aligned}
$$

This exposes a human-readable obstruction before any nontrivial complex-phase system is solved and compresses the finite verification to $23$ support-orbit representatives with tiny exact symbolic cores.

A future result that proves the singleton-forcing statement without finite enumeration, or that extends an analogous fiber obstruction to a broader edge model, would materially strengthen the structural interpretation. No such extension is claimed here.

## 11. Conclusion

We established a complete computer-assisted nonexistence theorem for a restricted fixed-endpoint-colour simple $K_6,D=3$ perfect-matching model and isolated the common structural obstruction behind its finite certificates. The three monochromatic unit-amplitude equations force three pairwise edge-disjoint nonzero witnesses and a nine-edge nonzero backbone. Their union has only two possible geometries. After symmetry reduction, all remaining supports fall into $23$ orbits.

Direct exhaustive inherited-colouring enumeration proves that every one of those support classes forces a mixed nonzero singleton fiber, while an exact symbolic verifier independently certifies singleton-avoidance contradictions with minimum cores of size at most three. A mixed singleton has no nonzero cancellation partner, so the required mixed amplitude cannot vanish. The contradiction therefore occurs already at the support-and-fiber level within this restricted model.

The result is intentionally scoped as a transparent calibration theorem and reproducible computer-assisted certificate. It does not resolve the unrestricted Krenn-Gu conjecture, but it provides a compact mechanism that can be inspected by humans and rerun with modest computational resources.

## Acknowledgement and disclosure statement

Public showcase copy: author contact and administrative metadata are intentionally omitted. All mathematical and computational claims in this display package are accompanied by reproducible source code and captured verifier output.

## References

[1] M. Krenn, X. Gu, and D. Soltész, *Questions on the Structure of Perfect Matchings inspired by Quantum Physics*, Proceedings of the 2nd Croatian Combinatorial Days, 57-70, 2019. DOI: 10.5592/CO/CCD.2018.05. arXiv:1902.06023.

[2] L. Sunil Chandran, R. Gajjala, and A. M. Illickan, *Krenn-Gu Conjecture for Sparse Graphs*, 49th International Symposium on Mathematical Foundations of Computer Science (MFCS 2024), LIPIcs 306, 41:1-41:15, 2024. DOI: 10.4230/LIPIcs.MFCS.2024.41.

[3] L. Sunil Chandran and R. Gajjala, *Edge-Coloured Graphs with only Monochromatic Perfect Matchings and Their Connection to Quantum Physics*, The Electronic Journal of Combinatorics 33(3), #P3.21, 2026. DOI: 10.37236/12573.

[4] algal, *A Lean proof of the Krenn-Gu $(6,3)$ case*, public verification repository `krenn-gu-6x3-certificate`, 2026, verified release dated 24 July 2026. Software/formal-proof artifact; accessed 21 September 2026.
