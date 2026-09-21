# Ebi wheat-arb margin screen (episode 111594513, seat0)

- Arbitraged (FIFO-matched buy->sell) units: 6533
- Net round-trip cash: -15,045 | weighted margin: -2.30 px/unit
- Matched lots profitable: 12/208
- Obs WHEAT price path min..max: 22..49

| buy-window (6d) | units | net px |
|---|---|---|
| d1-6 | 36 | 15 |
| d7-12 | 39 | 273 |
| d13-18 | 2045 | -5,984 |
| d19-24 | 2271 | -5,003 |
| d25-30 | 2142 | -4,346 |

Caveat: obs[t] is post-action, so buy px already includes Ebi's own demand
impact and sell px includes his supply impact -> computed spread UNDERSTATES
impact-free opportunity for buys, OVERSTATES nothing; a same-scale copycat
would move the price at least as much (self-impact law, E57c).