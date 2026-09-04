# Farming Score V3: Replay Revised

This notebook preserves the supplied two-route policy while converting its native C++ deployment into one standalone Python agent.

At turn 360, route 1 is selected precisely when the first shop is `BAKERY` and fertilizer market inventory is at most $10232$, or when the first shop is `PET_CAFE` and the rival has at most $64$ planted tiles. Only turns 360 through 431 differ between the routes.

At every 72-turn boundary, the affordability guard computes the selected block's planned purchase cost. If necessary, it protects required feed, fertilizer, and unplaced animals, then sells only surplus products in descending current-price order.

Running the code cell produces:

- `main.py`: the complete agent, with both compressed action tapes and no external dependency;
- `submission.tar.gz`: a deterministic standard submission containing only `main.py` at its root.
