# Installation-only runs — no transactions

The first named-cohort runs stopped during tool installation, before wallet
creation or deployment. npm selected `viem@2.57.10`, whose tarball returned 404.

- [Uniform 39741388638](https://github.com/moorisi/fault-weave/actions/runs/39741388638)
- [Trusted core 39741394867](https://github.com/moorisi/fault-weave/actions/runs/39741394867)
- [Impossible 39741411933](https://github.com/moorisi/fault-weave/actions/runs/39741411933)

Proof tooling now uses `npm ci` with a committed dependency lock, GenLayer CLI
0.39.2, genlayer-js 1.1.8, and viem 2.56.3. The latter tarball was verified available
from the official registry. This repair changes no contract bytes, fixture,
consensus condition or expected onchain result. These runs contribute zero receipts
to the primary proof count.
