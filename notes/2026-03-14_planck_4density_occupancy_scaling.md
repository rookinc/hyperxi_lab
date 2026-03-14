# Planck 4-Density Occupancy Scaling
Date: 2026-03-14

## Purpose

Record the current information-density ansatz and the resulting occupancy
scaling for particles and coherent masses.

## Postulate

Assume a maximal lawful information density of

\[
\rho_I^{\max} = 1 \text{ bit} / l_P^4.
\]

Interpretation: the primitive bookkeeping unit is a spacetime 4-cell, not
a purely spatial voxel.

## Coherent occupancy model

For mass \(M\), coherence length \(L\), and coherence time \(L/c\), define

\[
f_{\mathrm{occ}}(M,L)
=
\frac{Mc^2(L/c)/\hbar}{L^4/l_P^4}.
\]

This becomes

\[
f_{\mathrm{occ}}(M,L)
=
\frac{M}{m_P}\left(\frac{l_P}{L}\right)^3.
\]

This is the central scaling law.

## Reduced Compton specialization

For reduced Compton coherence,

\[
L = \bar{\lambda}_C = \frac{\hbar}{Mc},
\]

so

\[
L = l_P \frac{m_P}{M}.
\]

Substituting into the general law gives

\[
f_{\mathrm{occ}}
=
\frac{M}{m_P}
\left(\frac{l_P}{l_P(m_P/M)}\right)^3
=
\frac{M}{m_P}\left(\frac{M}{m_P}\right)^3
=
\left(\frac{M}{m_P}\right)^4.
\]

Thus

\[
\boxed{
f_{\mathrm{occ}} = \left(\frac{M}{m_P}\right)^4
}
\]

for one reduced Compton cycle.

## Consequences

### Electron

\[
f_{\mathrm{occ},e} \sim \left(\frac{m_e}{m_P}\right)^4 \approx 3.07\times 10^{-90}.
\]

### Proton

\[
f_{\mathrm{occ},p} \sim \left(\frac{m_p}{m_P}\right)^4 \approx 3.49\times 10^{-77}.
\]

### Ratio

\[
\frac{f_{\mathrm{occ},p}}{f_{\mathrm{occ},e}}
=
\left(\frac{m_p}{m_e}\right)^4
\approx 1.14\times 10^{13}.
\]

So the proton is about 13 orders of magnitude denser than the electron under
this bookkeeping, even though the mass ratio is only about 1836.

### Planck mass

\[
f_{\mathrm{occ}}(m_P)=1.
\]

So the Planck mass is the natural unit-occupancy threshold in this model.

## Interpretation

Under this ansatz:

- an electron is an extremely sparse recursive occupancy pattern,
- a proton is still sparse, but vastly denser,
- a Planck-mass reduced-Compton-scale object is order-one occupied.

This motivates the interpretation:

> mass measures 4-volume compression of one action quantum.

## Threshold coherence scale for general mass

Setting \(f_{\mathrm{occ}}=1\) gives

\[
L_\ast(M)=l_P\left(\frac{M}{m_P}\right)^{1/3}.
\]

This is the coherence length required for a mass \(M\) to reach unit occupancy.

## Working interpretation

The ansatz appears to separate three regimes:

1. ordinary matter: deeply sub-saturation,
2. Planck frontier: order-one occupancy,
3. beyond-Planck compression: geometry likely cannot ignore occupancy.

This may provide a route toward an information-density interpretation of
gravitational response.
