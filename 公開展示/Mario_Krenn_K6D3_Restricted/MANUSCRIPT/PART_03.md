No assignment passes. All $13$ triangular-prism support representatives and all $10$ $K_{3,3}$ representatives are singleton-forcing. The direct verifier checks

$$
1,217,855 \qquad (14)
$$

semantically distinct endpoint-colour assignments in total and terminates with exit code $0$. Therefore every admissible completion contains a mixed nonzero singleton fiber. $\square$

### Corollary 7 (Phase-independent obstruction)

Within this restricted model, the final contradiction does not require solving any nontrivial complex-phase cancellation equations.

**Proof.** Theorem 6 provides a mixed singleton fiber. Lemma 5 shows that the associated amplitude is a single nonzero monomial. There is no second nonzero term whose phase could cancel it. $\square$

The statement is deliberately narrow: complex weights are not irrelevant to the general Krenn-Gu problem. Rather, complex phases cannot repair a mixed fiber containing exactly one nonzero monomial.

## 7. Certificate route: exact symbolic contradiction cores

The second verifier certifies the same finite domain using exact endpoint-colour equality systems rather than direct bucket enumeration.

For a fixed support, let $\mathcal A$ be the surviving perfect matchings. For each $M\in\mathcal A$, absence of a mixed singleton would require at least one of the following alternatives:

1. $\Phi(M)$ is monochromatic; or
2. there exists another $M'\in\mathcal A$, $M'\neq M$, with $\Phi(M')=\Phi(M)$.

Each alternative is an exact coordinate-equality system among the twelve free endpoint-colour slots and constants $0,1,2$. A disjoint-set union structure checks consistency exactly; no floating point arithmetic, random search, complex-weight optimization, or approximate amplitude evaluation is used.

For each of the $23$ support-orbit representatives, the verifier searches subsets of one, two, or three surviving perfect matchings and finds a set whose singleton-avoiding alternatives are jointly inconsistent. The minimum-core-size distribution is

$$
15\text{ cases of size }1,
\qquad
6\text{ cases of size }2,
\qquad
2\text{ cases of size }3. \qquad (15)
$$

Thus

$$
\max(\text{minimum core size})=3. \qquad (16)
$$

For the two full-support representatives, the exact filtered alternative products are especially small:

$$
5\cdot7\cdot2=70
$$

joint combinations for the triangular-prism core, and

$$
3\cdot7\cdot7=147
$$

for the $K_{3,3}$ core; every one is inconsistent.

The symbolic verifier terminates with exit code $0$ and reports

$$
23/23\text{ support-orbit representatives UNSAT}. \qquad (17)
$$

This route does not numerically search $\mathbb C^{15}$. It proves exact combinatorial inconsistency of all endpoint-colour arrangements that would be required to avoid the singleton obstruction.

## 8. Unified nonexistence theorem

### Theorem 8 (Restricted-model nonexistence)

There is no assignment of fixed endpoint colours and complex edge weights on simple $K_6$ satisfying all three monochromatic target amplitudes and all mixed zero-amplitude equations.

**Proof.** Lemmas 1-2 and Corollary 3 reduce every hypothetical solution to one of the two witness geometries and one of the $23$ support orbits. The direct verifier proves that every such completion has a mixed nonzero singleton fiber. By Lemma 5, the corresponding mixed amplitude is nonzero, contradicting (4). The symbolic verifier independently certifies the impossibility of singleton avoidance on the same complete finite domain by exact equality contradictions with cores of size at most three. $\square$

The two programs are **materially different finite verification routes sharing the same public mathematical reduction**, not two logically unrelated proofs. Their agreement provides a cross-check against implementation-specific failure modes while the analytic lemmas make clear where the restricted-model assumptions enter.

## 9. Evidence levels and reproducibility

To keep analytic and computational claims separate, the proof dependencies are summarized below.

| Claim | Evidence level | Role |
|---|---|---|
| One nonzero witness per monochromatic colour | Analytic proof | Consequence of $A(a^6)=1$ |
| Pairwise edge-disjointness of witnesses | Analytic proof | Uses one fixed endpoint-colour pair per primitive edge |
| Nine forced nonzero edges | Analytic proof | Nonzero witness monomials |
| $80=60+20$ witness triples | Analytic finite counting | Complete witness-union classification |
| $64\to13$ and $64\to10$ support-orbit reductions | Exact finite computation, reconstructed by both programs | Complete support classification |
| Every completion has a mixed singleton fiber | Direct exhaustive enumeration | Structural universal step |
| Every support orbit has exact singleton-avoidance contradiction core $\le3$ | Symbolic exact computation | Independent finite cross-check |
| Mixed singleton contradicts $A(c)=0$ | Analytic proof | Final amplitude contradiction |

A clean rerun on 21 September 2026 produced the following release results:

- symbolic verifier: wall time approximately $0.66$ s, exit code $0$;
- direct verifier: wall time approximately $18.33$ s, exit code $0$;
- direct semantic assignments checked: $1,217,855$;
- final support representatives: $23/23$ impossible in both routes.

The supplementary archive contains both verifier programs, captured standard output, timing records, environment information, a machine-readable manifest, and SHA-256 hashes.

## 10. Scope boundary and relation to prior work

The restriction to one primitive edge per unordered vertex pair is essential. In the unrestricted inherited-colouring problem, the graph need not be simple and multiple edges with different endpoint-colour types may occur between the same two vertices [1]. In that setting, monochromatic witnesses of different colours can use the same vertex pair through different primitive edge types, so Lemma 2 does not apply in its present form.

Consequently, Theorems 6 and 8 must not be relabelled as results for the unrestricted graph model. In particular, this paper does not claim to settle the general Krenn-Gu conjecture.

Broader special cases and sparse regimes have been studied by other methods [2,3]. In 2026, a public Lean-checked certificate established the stronger unrestricted $(6,3)$ nonexistence theorem over the full $135$ coloured edge-type variables and $729$ inherited-colouring equations [4]. That formal result covers a strictly larger model than the one studied here.
