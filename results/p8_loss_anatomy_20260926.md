# P8 live loss anatomy — 2026-09-26 field (144 h1q6 episodes)

## LOSSES (winner-minus-ours, positive = winner did more)  n=63

| feature | n | median gap | mean gap | #games winner>ours |
|---|---:|---:|---:|---:|
| sell_ops | 63 | +2 | +8.5 | 32 |
| sell_by.MILK | 63 | -1 | +16.2 | 30 |
| sell_by.STRAWBERRY | 63 | +1 | +207.2 | 34 |
| sell_units | 63 | -1 | +1800.3 | 30 |
| animals.COW | 63 | +0 | +0.1 | 4 |
| animals.GOOSE | 63 | +0 | +0.2 | 3 |
| animals.SHEEP | 63 | +0 | -0.0 | 1 |
| buy_seed.CARROT | 63 | +0 | -1.0 | 9 |
| buy_seed.MELON | 63 | +0 | +0.3 | 4 |
| buy_seed.STRAWBERRY | 63 | +0 | -0.2 | 1 |
| buy_seed.TOMATO | 63 | +0 | +0.4 | 5 |
| buy_seed.WHEAT | 63 | +0 | -0.9 | 16 |
| feed | 63 | +0 | +0.5 | 3 |
| fert | 63 | +0 | +6.1 | 13 |
| hire | 63 | +0 | +0.2 | 8 |
| land | 63 | +0 | -0.1 | 0 |
| plant.CARROT | 63 | +0 | -0.9 | 7 |
| plant.MELON | 63 | +0 | +0.1 | 3 |
| plant.STRAWBERRY | 63 | +0 | -0.3 | 3 |
| plant.TOMATO | 63 | +0 | +0.3 | 5 |
| plant.WHEAT | 63 | +0 | +1.3 | 20 |
| sell_by.CARROT | 63 | +0 | +553.6 | 13 |
| sell_by.EGG | 63 | +0 | +276.7 | 12 |
| sell_by.FERTILIZER | 63 | +0 | -30.9 | 15 |
| sell_by.MELON | 63 | +0 | +221.8 | 6 |
| sell_by.SHEEP | 63 | +0 | +0.1 | 1 |
| sell_by.TOMATO | 63 | +0 | +209.7 | 7 |
| sell_by.WHEAT | 63 | +0 | +138.7 | 24 |
| sell_by.WOOL | 63 | +0 | +207.1 | 21 |
| water | 63 | +0 | -5.7 | 10 |

## WINS (winner-minus-ours, control)  n=65

| feature | n | median gap | mean gap | #games winner>ours |
|---|---:|---:|---:|---:|
| sell_units | 65 | -10 | -172.5 | 25 |
| sell_ops | 65 | -4 | -6.0 | 18 |
| sell_by.MILK | 65 | +3 | +170.1 | 36 |
| sell_by.WHEAT | 65 | +2 | -0.8 | 33 |
| sell_by.STRAWBERRY | 65 | +1 | +93.9 | 33 |
| animals.COW | 65 | +0 | +0.1 | 2 |
| animals.GOOSE | 65 | +0 | +0.2 | 3 |
| animals.SHEEP | 65 | +0 | -0.0 | 2 |
| buy_seed.CARROT | 65 | +0 | -1.5 | 9 |
| buy_seed.MELON | 65 | +0 | +0.0 | 1 |
| buy_seed.STRAWBERRY | 65 | +0 | -0.2 | 0 |
| buy_seed.TOMATO | 65 | +0 | -0.4 | 3 |
| buy_seed.WHEAT | 65 | +0 | +0.4 | 22 |
| feed | 65 | +0 | +0.7 | 2 |
| fert | 65 | +0 | +1.5 | 14 |
| hire | 65 | +0 | +0.1 | 6 |
| land | 65 | +0 | -0.1 | 1 |
| plant.CARROT | 65 | +0 | -1.8 | 8 |
| plant.MELON | 65 | +0 | +0.0 | 1 |
| plant.STRAWBERRY | 65 | +0 | -0.2 | 0 |
| plant.TOMATO | 65 | +0 | -0.4 | 3 |
| plant.WHEAT | 65 | +0 | +1.2 | 22 |
| sell_by.CARROT | 65 | +0 | -4.9 | 16 |
| sell_by.EGG | 65 | +0 | +4.1 | 12 |
| sell_by.FERTILIZER | 65 | +0 | -496.1 | 12 |
| sell_by.MELON | 65 | +0 | +0.1 | 1 |
| sell_by.TOMATO | 65 | +0 | -3.6 | 3 |
| sell_by.WOOL | 65 | +0 | +64.8 | 26 |
| water | 65 | +0 | -5.9 | 8 |

## Lever check (loss-gap median vs win-gap median)

- fert: loss-gap +0, win-gap +0
- water: loss-gap +0, win-gap +0
- sell_units: loss-gap -1, win-gap -10
- sell_ops: loss-gap +2, win-gap -4
- animals.COW: loss-gap +0, win-gap +0
- animals.SHEEP: loss-gap +0, win-gap +0
- animals.GOOSE: loss-gap +0, win-gap +0
- land: loss-gap +0, win-gap +0
- hire: loss-gap +0, win-gap +0
- plant.WHEAT: loss-gap +0, win-gap +0
- plant.CARROT: loss-gap +0, win-gap +0
- plant.STRAWBERRY: loss-gap +0, win-gap +0
- plant.TOMATO: loss-gap +0, win-gap +0
- plant.MELON: loss-gap +0, win-gap +0
- sell_by.FERTILIZER: loss-gap +0, win-gap +0
- sell_by.WHEAT: loss-gap +0, win-gap +2