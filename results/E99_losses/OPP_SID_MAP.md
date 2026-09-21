# OPP_SID_MAP — who is beating us live (2026-09-21 ~16:05 UTC snapshot)

Method: sid -> teamId via `ListEpisodes` (EpisodeService private API, same auth as
tools/find_top10_sids.py / tools/fetch_episodes.py); teamId -> name/rank via full
leaderboard CSV (`kaggle competitions leaderboard kaggriculture -d`).
Names for 56401171 / 56386266 were already known from results/E98F/live_eps/opp_forensics.json.

## Sid -> team map

| sid | team (teamId) | user(s) | LB rank / score | evidence | prior encounters in our files |
|---|---|---|---|---|---|
| 56428201 | **offhand** (16929873) | offhand | 196 / 2741.2 | ListEpisodes teamId + LB CSV | E94 ep 111672968 loss, delta -20908 (opp reward 122321 vs our 101413) |
| 56426176 | **JinboWang** (16889791) | jinbowang1 | 127 / 2786.6 | ListEpisodes + LB CSV | E94 ep 111645900 loss, delta -20300 (132672 vs 112372) |
| 56386266 | **Ebi** (16882725) | ebinan92 | **31 / 2912.9** | opp_forensics.json (E98F) + LB CSV | E98F ep 111594513 loss, delta -17397 (111857 vs 94460); also in E94 summary |
| 56421005 | **A. R. SEKKAT** (16748765) | arsekkat | 136 / 2778.9 | ListEpisodes + LB CSV | E94 ep 111604665 loss, delta -12996 (118123 vs 105127) |
| 56418088 | **Crop Dustas** (16714457) | peikopon, rishigottumukkala | 1669 / 2033.2 | ListEpisodes + LB CSV | E94 ep 111612464 loss, delta -9498 (117390 vs 107892) |
| 56401171 | **sue124** (16779977) | ryotasueyoshi | 483 / 2620.1 | opp_forensics.json (E98F) + LB CSV | E98F ep 111596738 loss, delta -5585 (111890 vs 106305); also in E94 summary |
| 56424408 | **Tariq Alyami** (16833013) | tariqalyami | 2088 / 1757.2 | ListEpisodes + LB CSV | Apex ep 111675922 — we WON (89853 vs our 100283); frequent opponent in APEX_live_eps |
| 56433319 | **alban** (16679214) | albantiacoh | 311 / 2682.0 | ListEpisodes + LB CSV | Apex ep 111662271 — Apex's ONLY loss (124092 vs 122619, delta -1473 — narrow) |

Notes:
- All 8 sids identified; none anonymous.
- Crop Dustas and Tariq Alyami have low LB scores (their board entry is from an older/other
  selected submission), but the specific sids above played strong episodes vs us — treat their
  episode rewards, not board score, as the signal.
- Ebi (rank 31) is the only true top-35 opponent among the beaters; the -17397 margin loss to
  Ebi is the most concerning. JinboWang (127), SEKKAT (136), offhand (196), alban (311) are the
  2600-2800 band just above us.
- No prior mentions of these team names anywhere in results/*.md or docs/ — first identification.

## Leaderboard top-20 snapshot (2026-09-21T16:05Z, public CSV, 9755 teams)

| # | teamId | team | score |
|---|---|---|---|
| 1 | 16732748 | DSM | 3130.0 |
| 2 | 16718819 | Majkel1337 | 3107.8 |
| 3 | 16730612 | Unknown Mother-Goose | 3053.1 |
| 4 | 16770421 | Vadim Vasilenko | 3052.5 |
| 5 | 16640510 | SpaTaro | 3049.2 |
| 6 | 16730524 | THIRD FARM CLUB | 3048.6 |
| 7 | 16654697 | KawattaTaido | 3045.7 |
| 8 | 16732403 | ymg_aq | 3036.6 |
| 9 | 16817528 | QQ | 3002.6 |
| 10 | 16760569 | Otter Vibe | 2998.2 |
| 11 | 16758882 | mtmr_s1 | 2996.0 |
| 12 | 16760701 | Yannik Schiffner | 2973.8 |
| 13 | 16675778 | Orbital Terraformer | 2969.8 |
| 14 | 16854176 | 吃白饭的大肥鱼 | 2968.3 |
| 15 | 16621799 | Artem The Farmer | 2966.7 |
| 16 | 16622198 | THUNDER THUNDER | 2962.0 |
| 17 | 16673205 | Arda Ceylan | 2960.0 |
| 18 | 16793083 | seek inspiration | 2958.0 |
| 19 | 16632327 | midnq | 2949.7 |
| 20 | 16887437 | TheEggman | 2948.6 |

Top-10 cut is now ~2998 (was ~3020); top-1 DSM 3130 (Majkel1337 dropped from 3234 to 3107.8).
The whole top of the board decayed ~60-130 pts vs the previous snapshot — scores are rolling.

## Where our submissions rank

Us = **Shivam_2212** (teamId 16669256, user shivam2212), SubmissionCount 2.

- **Rank 325, board score 2678.2** — this is E94 (sid 56422679). It is our currently
  displayed/selected score.
- r78u (56405541, last-known 2722.5), metav4_early (56387781, 2781.9), Apex (56433342, 1836.6)
  do NOT appear as separate LB rows — the public board only shows the best selected submission
  per team. Those values are episode-time rewards/ratings, not board scores; only 2 submissions
  count and the board currently reflects 2678.2.
- Band context: rank 325 sits ~330 pts below the top-10 cut (~2998) and ~250 below Ebi (2912.9,
  rank 31). The 2700-2800 band (ranks ~120-200: JinboWang, SEKKAT, offhand) is the immediate
  ceiling our E94 losses are coming from.
