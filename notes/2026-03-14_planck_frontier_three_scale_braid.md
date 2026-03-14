# Planck Frontier as a Three-Scale Braid
Date: 2026-03-14

## Purpose

Record the three characteristic length scales arising from the current
information-density ansatz and compare their crossing masses.

## Ansatz

Assume a maximal lawful information density of

\[
\rho_I^{\max} = 1 \text{ bit} / l_P^4
\]

with \(l_P\) the Planck length, interpreted as a spacetime 4-cell scale.

For a coherent mass \(M\) spread over spatial scale \(L\) and time \(L/c\),
define the occupancy

\[
f_{\mathrm{occ}}(M,L)
=
\frac{Mc^2(L/c)/\hbar}{L^4/l_P^4}.
\]

This simplifies to

\[
f_{\mathrm{occ}}(M,L)
=
\frac{M}{m_P}\left(\frac{l_P}{L}\right)^3
\]

using \(\hbar/(m_P c)=l_P\).

## Unit-occupancy coherence scale

Setting \(f_{\mathrm{occ}}=1\) gives the threshold coherence scale

\[
L_\ast(M)=l_P\left(\frac{M}{m_P}\right)^{1/3}.
\]

## Three scales

Let

\[
x := \frac{M}{m_P}.
\]

Then the three comparison scales are:

### Reduced Compton wavelength

\[
\bar{\lambda}_C(M)=\frac{\hbar}{Mc}=l_P x^{-1}.
\]

### Occupancy-threshold coherence scale

\[
L_\ast(M)=l_P x^{1/3}.
\]

### Schwarzschild radius

\[
R_s(M)=\frac{2GM}{c^2}=2l_P x.
\]

## Pairwise crossings

### Compton = occupancy

\[
\bar{\lambda}_C = L_\ast
\iff
l_P x^{-1} = l_P x^{1/3}
\iff
x=1.
\]

Therefore

\[
M = m_P,
\qquad
\bar{\lambda}_C = L_\ast = l_P.
\]

### Compton = Schwarzschild

\[
\bar{\lambda}_C = R_s
\iff
l_P x^{-1} = 2 l_P x
\iff
x = \frac{1}{\sqrt{2}}.
\]

Therefore

\[
M = \frac{m_P}{\sqrt{2}},
\qquad
\bar{\lambda}_C = R_s = \sqrt{2}\, l_P.
\]

### Occupancy = Schwarzschild

\[
L_\ast = R_s
\iff
l_P x^{1/3} = 2 l_P x
\iff
x = \frac{1}{2\sqrt{2}}.
\]

Therefore

\[
M = \frac{m_P}{2\sqrt{2}},
\qquad
L_\ast = R_s = \frac{l_P}{\sqrt{2}}.
\]

## Conclusion

The three scales do not meet at a single point. Instead they cross across a
narrow Planck-scale mass band:

\[
\frac{m_P}{2\sqrt{2}}
<
\frac{m_P}{\sqrt{2}}
<
m_P.
\]

This suggests that the “Planck frontier” is not a single threshold but a
three-scale braid in which:

1. occupancy threshold crosses Schwarzschild first,
2. Compton crosses Schwarzschild second,
3. Compton meets occupancy at the top end, at \(M=m_P\).

## Ordering by mass regime

For \(0 < x < 1/(2\sqrt{2})\):

\[
\bar{\lambda}_C > L_\ast > R_s.
\]

For \(1/(2\sqrt{2}) < x < 1/\sqrt{2}\):

\[
\bar{\lambda}_C > R_s > L_\ast.
\]

For \(1/\sqrt{2} < x < 1\):

\[
R_s > \bar{\lambda}_C > L_\ast.
\]

For \(x > 1\):

\[
R_s > L_\ast > \bar{\lambda}_C.
\]

## Working interpretation

This provides a possible bridge between:

- quantum localization scale,
- recursive information-density threshold,
- gravitational collapse scale.

The Planck mass is then interpreted not as a single magic point, but as the
upper end of a short transition ladder.
