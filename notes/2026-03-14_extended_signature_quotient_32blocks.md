# Extended Signature Quotient on the Lowest 32 Eigenspace Blocks

## Summary

Extending the signature-transition quotient from the lowest 20 eigenspace blocks to the lowest 32 eigenspace blocks enlarges the observed signature alphabet from 5 classes to 8 classes.

The 20-block quotient was therefore a low-energy truncation, not the full signature quotient presently visible in the local transport algebra.

## Input data

The extension was built from:

- `reports/spectral/generator_sign_reps.json`
- `reports/spectral/block_transitions/low_block_transition_graph_032_blocks.json`

using:

- `scripts/decompose_generator_sign_reps.py --n 32`
- `scripts/build_low_block_transition_graph.py --n 32`
- `scripts/extend_signature_quotient_to_n_blocks.py --n 32`

## Observed signature classes

The lowest 32 eigenspace blocks split into the following 8 signature sectors:

- `(+I,+I,+I)` blocks = `[25, 26, 27, 30, 31, 32]`
- `(+I,+I,-I)` blocks = `[18, 20, 23, 24]`
- `(+I,-I,+I)` blocks = `[28, 29]`
- `(+I,-I,-I)` blocks = `[10, 11, 12, 13, 14, 16, 17]`
- `(-I,+I,+I)` blocks = `[21, 22]`
- `(-I,+I,-I)` blocks = `[5, 7, 8]`
- `(-I,-I,+I)` blocks = `[15, 19]`
- `(-I,-I,-I)` blocks = `[1, 2, 3, 4, 6, 9]`

## Main structural conclusion

The earlier 5-sector quotient captured only the lowest-signature front of the transport algebra.

Once blocks 21 through 32 are included, three additional sectors appear:

- `(+I,+I,+I)`
- `(+I,-I,+I)`
- `(-I,+I,+I)`

This shows that the signature flow is not exhausted by the low-energy parity-adjacent picture.

## Stationary distribution

The 32-block quotient gives the following stationary weights:

- `(+I,-I,-I)` = `0.244137`
- `(-I,-I,-I)` = `0.192399`
- `(+I,+I,+I)` = `0.184696`
- `(+I,+I,-I)` = `0.116029`
- `(-I,+I,-I)` = `0.106012`
- `(-I,+I,+I)` = `0.061523`
- `(-I,-I,+I)` = `0.060332`
- `(+I,-I,+I)` = `0.034873`

## Interpretation

Two earlier low sectors remain dominant:

- `(+I,-I,-I)`
- `(-I,-I,-I)`

But the fully positive sector `(+I,+I,+I)` now appears as a major reservoir, with stationary weight comparable to the strongest negative sectors.

This is the key conceptual upgrade from the 20-block quotient:
the fully positive signature sector is not peripheral once the quotient is extended.

## Strongest outgoing transitions

The strongest outgoing edge from each signature sector is:

- `(+I,+I,+I) -> (+I,-I,-I)` with `p = 0.297319`
- `(+I,+I,-I) -> (+I,-I,-I)` with `p = 0.250559`
- `(+I,-I,+I) -> (+I,+I,-I)` with `p = 0.231752`
- `(+I,-I,-I) -> (+I,+I,+I)` with `p = 0.188336`
- `(-I,+I,+I) -> (+I,-I,-I)` with `p = 0.298126`
- `(-I,+I,-I) -> (+I,-I,-I)` with `p = 0.213145`
- `(-I,-I,+I) -> (-I,-I,-I)` with `p = 0.325713`
- `(-I,-I,-I) -> (+I,+I,+I)` with `p = 0.158543`

## Reading of the flow

At the 32-block level, the quotient is better described as a multi-basin signature flow network than as a simple parity-adjacency skeleton.

The dominant qualitative features are:

1. `(+I,-I,-I)` acts as a major receiving sector.
2. `(-I,-I,-I)` remains a strong anchor sector.
3. `(+I,+I,+I)` becomes a substantial high-signature reservoir.
4. `(+I,-I,+I)` remains comparatively light and sparse.

## Provisional meaning

The low-energy quotient was real, but incomplete.

The extended quotient suggests that transport reorganizes across a broader signed sector geometry in which positive-positive-positive blocks participate strongly in the long-run flow. This means the local transport algebra is not merely splitting into “negative core plus adjacent corrections,” but into a richer directed ecology of signature sectors.

## Immediate next step

Run the same three companion analyses on the 32-block quotient:

- random walk
- cycle extraction
- effective Hamiltonian fit

using:

- `signature_transition_quotient_032_blocks.json`

This will show whether the 8-sector system inherits the same dominant cycle architecture as the 5-sector quotient, or whether new metastable loops emerge once the higher positive sectors are admitted.
