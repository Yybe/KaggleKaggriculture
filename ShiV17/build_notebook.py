# -*- coding: utf-8 -*-
"""Builds ShiV17_open_source.ipynb — a polished, publication-grade Kaggle notebook.

All benchmark numbers are the VERIFIED results from real head-to-head runs on
kaggle-environments 1.32.6 (townCenterSellInterval=24, frozen 8-seed gate family,
8 seeds x 2 seats = 16 games). Nothing is invented.
"""
import json
import textwrap


# ----------------------------------------------------------------------------
# Palette (deep indigo hero, emerald wins, coral losses, amber accents)
# ----------------------------------------------------------------------------
HERO_GRAD = "linear-gradient(135deg,#140b2e 0%,#2a1a5e 55%,#4c1d95 100%)"
INDIGO = "#6d28d9"
INDIGO_SOFT = "#ede9fe"
VIOLET = "#8b5cf6"
EMERALD = "#10b981"
EMERALD_BG = "#d1fae5"
CORAL = "#f43f5e"
CORAL_BG = "#ffe4e6"
AMBER = "#f59e0b"
AMBER_BG = "#fef3c7"
INK = "#1e293b"
MUTED = "#64748b"
CARD = "#ffffff"
PAGE = "#f8fafc"
BORDER = "#e2e8f0"


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": textwrap.dedent(src).strip()}


def code(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": textwrap.dedent(src).strip(),
    }


cells = []

# ============================================================================
# 1. HERO BANNER
# ============================================================================
cells.append(md(f"""
<div style="background:{HERO_GRAD};border-radius:18px;padding:52px 32px 44px 32px;margin:0 0 18px 0;color:#ffffff;text-align:center;font-family:Arial,Helvetica,sans-serif;box-shadow:0 18px 40px rgba(76,29,149,0.35);">
  <div style="font-size:12px;letter-spacing:4px;text-transform:uppercase;color:#c4b5fd;margin-bottom:14px;">Kaggriculture &middot; Agent Post-Mortem</div>
  <h1 style="margin:0;font-size:46px;font-weight:800;letter-spacing:1px;line-height:1.1;">ShiV17 &mdash; The Boatlee Slayer</h1>
  <p style="margin:16px auto 0 auto;max-width:760px;font-size:18px;line-height:1.6;color:#e0e7ff;">
    We found the one fixed constant inside the "unbeatable" V16-RC2 meta &mdash;
    a 3-turn fertilizer market relay &mdash; and front-ran it by two turns.
    A 0% win rate against the tape lords became <b style="color:#6ee7b7;">93.8%</b>.
  </p>
  <div style="margin-top:26px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">
    <span style="display:inline-block;background:#10b981;color:#ffffff;padding:9px 20px;border-radius:999px;font-weight:700;font-size:14px;">93.8% win rate</span>
    <span style="display:inline-block;background:#f59e0b;color:#451a03;padding:9px 20px;border-radius:999px;font-weight:700;font-size:14px;">+176 mean &Delta; vs boatlee</span>
    <span style="display:inline-block;background:#c4b5fd;color:#312e81;padding:9px 20px;border-radius:999px;font-weight:700;font-size:14px;">8 seeds &times; 2 seats &middot; 16 games</span>
  </div>
</div>
"""))

# ============================================================================
# 2. TL;DR SUMMARY CARDS
# ============================================================================
cells.append(md(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:24px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 16px 0;color:{INK};font-size:22px;">TL;DR &mdash; from getting farmed to farming the farmers</h2>
  <div style="display:flex;gap:14px;flex-wrap:wrap;">
    <div style="flex:1;min-width:220px;background:{PAGE};border:1px solid {BORDER};border-radius:12px;padding:16px;text-align:center;">
      <div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:{MUTED};">Record vs boatlee V16-RC2</div>
      <div style="font-size:26px;font-weight:800;color:{CORAL};margin-top:6px;">0W / 16L</div>
      <div style="font-size:18px;font-weight:800;color:{EMERALD};">&rarr; 15W / 1L</div>
    </div>
    <div style="flex:1;min-width:220px;background:{PAGE};border:1px solid {BORDER};border-radius:12px;padding:16px;text-align:center;">
      <div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:{MUTED};">Mean &Delta; vs boatlee</div>
      <div style="font-size:26px;font-weight:800;color:{CORAL};margin-top:6px;">&#8722;14,735</div>
      <div style="font-size:18px;font-weight:800;color:{EMERALD};">&rarr; +176</div>
    </div>
    <div style="flex:1;min-width:220px;background:{PAGE};border:1px solid {BORDER};border-radius:12px;padding:16px;text-align:center;">
      <div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:{MUTED};">Record vs kaitofukami v27</div>
      <div style="font-size:26px;font-weight:800;color:{CORAL};margin-top:6px;">0W / 16L</div>
      <div style="font-size:18px;font-weight:800;color:{EMERALD};">&rarr; 15W / 1L</div>
    </div>
    <div style="flex:1;min-width:220px;background:{PAGE};border:1px solid {BORDER};border-radius:12px;padding:16px;text-align:center;">
      <div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;color:{MUTED};">Mean &Delta; vs kaitofukami</div>
      <div style="font-size:26px;font-weight:800;color:{CORAL};margin-top:6px;">&#8722;13,639</div>
      <div style="font-size:18px;font-weight:800;color:{EMERALD};">&rarr; +3,587</div>
    </div>
  </div>
  <div style="margin-top:16px;background:{AMBER_BG};border:1px solid #fcd34d;border-radius:10px;padding:12px 16px;color:#78350f;font-size:14px;line-height:1.6;">
    <b>The whole trick in one sentence:</b> the strongest opponent player always sells its
    fertilizer exactly 3 turns before its own scheduled sale. We sell 5 turns before
    instead &mdash; capturing the peak price and leaving it to dump into a $1 market.
  </div>
</div>
"""))

# ============================================================================
# 3. TABLE OF CONTENTS
# ============================================================================
cells.append(md(f"""
<div style="background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 12px 0;color:{INK};font-size:20px;">Table of Contents</h2>
  <ol style="margin:0;color:{INK};font-size:15px;line-height:2.0;">
    <li><a href="#game" style="color:{INDIGO};text-decoration:none;font-weight:600;">The Game in 30 Seconds</a></li>
    <li><a href="#meta" style="color:{INDIGO};text-decoration:none;font-weight:600;">The Meta &mdash; Everyone Plays a Tape</a></li>
    <li><a href="#villain" style="color:{INDIGO};text-decoration:none;font-weight:600;">The Villain &mdash; boatlee V16-RC2 and its 3-Turn Relay</a></li>
    <li><a href="#flaw" style="color:{INDIGO};text-decoration:none;font-weight:600;">The Fatal Flaw &mdash; a Fixed Lead</a></li>
    <li><a href="#hero" style="color:{INDIGO};text-decoration:none;font-weight:600;">The Hero &mdash; ShiV17's 5-Turn Counter-Relay</a></li>
    <li><a href="#results" style="color:{INDIGO};text-decoration:none;font-weight:600;">Head-to-Head Results</a></li>
    <li><a href="#idea" style="color:{INDIGO};text-decoration:none;font-weight:600;">The Idea in 10 Lines</a></li>
    <li><a href="#limits" style="color:{INDIGO};text-decoration:none;font-weight:600;">What's Not in This Notebook</a></li>
  </ol>
</div>
"""))

# ============================================================================
# 4. THE GAME IN 30 SECONDS
# ============================================================================
cells.append(md(f"""
<div id="game" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {INDIGO};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:{INDIGO};font-size:24px;">1 &middot; The Game in 30 Seconds</h2>
  <p style="margin:0 0 12px 0;font-size:15px;line-height:1.7;color:{INK};">
    <b>Kaggriculture</b> is a 1v1, turn-based farming economy. Each player runs a
    10&times;10 farm over a fixed season of <b>720 turns</b> (30 days &times; 24 hourly steps).
    Every turn you move and command your farmer plus hired hands, manage the 100-slot
    shed, and batch market orders.
  </p>
  <ul style="margin:0;padding-left:22px;font-size:15px;line-height:1.9;color:{INK};">
    <li><b>Shared dynamic market.</b> Prices move with aggregate inventory through per-resource shape functions (linear, sq, sqrt, log) with a hard <b>$1 floor</b>.</li>
    <li><b>Win condition.</b> Most coins at the end of the season. Nothing else matters.</li>
    <li><b>Asymmetric information.</b> Both farms are visible every turn; your own shed, seeds and inventories are private.</li>
  </ul>
  <div style="margin-top:12px;background:{INDIGO_SOFT};border:1px solid #c4b5fd;border-radius:10px;padding:12px 16px;color:#4c1d95;font-size:14px;line-height:1.6;">
    <b>Why this matters:</b> because supply is shared and visible, <i>when</i> you sell is
    as important as <i>what</i> you sell. Dumping into a glut returns $1 a unit;
    selling into a thin market returns $100+.
  </div>
</div>
"""))

# ============================================================================
# 5. THE META
# ============================================================================
cells.append(md(f"""
<div id="meta" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {AMBER};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:#92400e;font-size:24px;">2 &middot; The Meta &mdash; Everyone Plays a Tape</h2>
  <p style="margin:0 0 12px 0;font-size:15px;line-height:1.7;color:{INK};">
    The engine is <b>deterministic</b>: two identical agents on the same seed tie
    exactly, every time (16/16). Because of that, the top of the leaderboard became
    a <b>tape war</b>. Every strong opponent plays a V14-lineage agent: a
    <b>precomputed 719-step hardcoded action route</b> with a low-entropy
    <code style="background:{AMBER_BG};border:1px solid #fcd34d;border-radius:5px;padding:1px 6px;">HIRE4</code>
    opening, rebuilt from the top public agent and replayed with near-clone precision.
  </p>
  <p style="margin:0;font-size:15px;line-height:1.7;color:{INK};">
    Our champion at the time &mdash; <b>V16a</b> &mdash; went <b>0W/16L</b> against the two
    strongest tape players: <b>boatlee V16-RC2</b> (mean &Delta; &#8722;14,735) and
    <b>kaitofukami v27</b> (mean &Delta; &#8722;13,639). boatlee itself beat kaitofukami
    15W/1L. The tape meta looked unbeatable.
  </p>
</div>
"""))

# ============================================================================
# 6. THE VILLAIN  (with SVG timeline of the 3-turn relay)
# ============================================================================
svg_relay = """
<svg viewBox="0 0 920 330" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:920px;height:auto;">
  <defs>
    <linearGradient id="crashGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="45%" stop-color="#ea580c"/>
      <stop offset="100%" stop-color="#dc2626"/>
    </linearGradient>
    <marker id="arrowCoral" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#e11d48"/>
    </marker>
  </defs>
  <rect x="10" y="10" width="900" height="310" rx="14" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
  <text x="460" y="44" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#1e293b">boatlee V16-RC2 &mdash; the 3-turn fertilizer market relay</text>
  <text x="460" y="66" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="12.5" fill="#64748b">one 24-step cycle: it sells everything 3 turns early, then the market crashes</text>

  <!-- price curve -->
  <polyline points="120,80 230,95 340,115 450,225 560,258 670,258 780,258"
            fill="none" stroke="url(#crashGrad)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- step 14: boatlee dump -->
  <line x1="340" y1="60" x2="340" y2="300" stroke="#e11d48" stroke-width="1.5" stroke-dasharray="5 4"/>
  <circle cx="340" cy="115" r="9" fill="#f43f5e"/>
  <text x="340" y="140" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#be123c">boatlee dumps ALL fertilizer</text>
  <text x="340" y="158" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#64748b">(sells at step%24 == 14)</text>

  <!-- step 17: scheduled sell -->
  <line x1="670" y1="60" x2="670" y2="300" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="5 4"/>
  <circle cx="670" cy="258" r="9" fill="#dc2626"/>
  <text x="670" y="290" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="bold" fill="#991b1b">mirror's scheduled sell &mdash; market at $1</text>
  <text x="670" y="308" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#64748b">(future_step%24 == 17, already crashed)</text>

  <!-- axis -->
  <line x1="120" y1="278" x2="780" y2="278" stroke="#cbd5e1" stroke-width="2"/>
  <text x="120" y="300" font-family="Arial,Helvetica,sans-serif" font-size="11.5" fill="#94a3b8">step 12</text>
  <text x="780" y="300" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="11.5" fill="#94a3b8">step 18</text>

  <!-- price labels -->
  <text x="120" y="74" font-family="Arial,Helvetica,sans-serif" font-size="11.5" font-weight="bold" fill="#b45309">&asymp;$100+</text>
  <text x="770" y="250" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="11.5" font-weight="bold" fill="#b91c1c">$1 floor</text>
</svg>
"""

cells.append(md(f"""
<div id="villain" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {CORAL};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:#be123c;font-size:24px;">3 &middot; The Villain &mdash; boatlee V16-RC2's 3-Turn Relay</h2>
  <p style="margin:0 0 12px 0;font-size:15px;line-height:1.7;color:{INK};">
    Reverse-engineering <code style="background:{CORAL_BG};border:1px solid #fecdd3;border-radius:5px;padding:1px 6px;">boatlee_v16rc2/main.py</code> revealed a 719-step
    hardcoded route hiding one weapon: a <b>guarded, debt-accounted fertilizer market
    relay</b> (<code style="background:{CORAL_BG};border:1px solid #fecdd3;border-radius:5px;padding:1px 6px;">_rc2_market_relay</code>).
  </p>
  <ul style="margin:0;padding-left:22px;font-size:15px;line-height:1.9;color:{INK};">
    <li>At steps <b>216 / 240 / 264</b> it compares a public farm-signature distance between the two farms. If the opponent is a near-mirror (distance &#8804; 8), it <b>locks on</b>.</li>
    <li>For every scheduled fertilizer sale that would land at <code style="background:{CORAL_BG};border:1px solid #fecdd3;border-radius:5px;padding:1px 6px;">future_step%24 == 17</code>, it sells <b>ALL</b> its fertilizer <b>3 turns early</b> &mdash; at <code style="background:{CORAL_BG};border:1px solid #fecdd3;border-radius:5px;padding:1px 6px;">step%24 == 14</code>.</li>
    <li>The effect: boatlee books a decent price for itself, then the aggregate inventory spike crashes the shared fertilizer price to <b>$1</b> right before the mirror's scheduled sell turn.</li>
  </ul>
  {svg_relay}
</div>
"""))

# ============================================================================
# 7. THE FATAL FLAW
# ============================================================================
cells.append(md(f"""
<div id="flaw" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {CORAL};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:#be123c;font-size:24px;">4 &middot; The Fatal Flaw &mdash; a Fixed Lead</h2>
  <p style="margin:0 0 12px 0;font-size:15px;line-height:1.7;color:{INK};">
    The relay's lead is <b>hardcoded to 3 turns</b>. boatlee will always dump at
    <code style="background:{CORAL_BG};border:1px solid #fecdd3;border-radius:5px;padding:1px 6px;">step%24 == 14</code>,
    regardless of the actual market state. That rigidity is the whole ballgame:
  </p>
  <div style="background:{CORAL_BG};border:1px solid #fecdd3;border-radius:10px;padding:14px 18px;margin:0 0 12px 0;color:#881337;font-size:15px;line-height:1.7;">
    If an opponent front-runs it with a <b>longer lead</b> (4 or 5 turns), they sell
    <i>before</i> boatlee &mdash; capturing the peak price &mdash; and crash the market to
    $1 <i>before boatlee's dump even executes</i>. boatlee's revenue plan collapses.
    Its debt-repayment logic (which expects a healthy price at the future step) makes
    the damage worse.
  </div>
  <div style="background:#f1f5f9;border:1px solid {BORDER};border-radius:10px;padding:12px 16px;color:{MUTED};font-size:13.5px;line-height:1.6;">
    <b>A fixed constant you can observe = a fix you can pre-empt.</b> The relay is only
    dangerous when nobody is watching the calendar.
  </div>
</div>
"""))

# ============================================================================
# 8. THE HERO  (with SVG contrast diagram)
# ============================================================================
svg_contrast = """
<svg viewBox="0 0 920 380" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:920px;height:auto;">
  <defs>
    <linearGradient id="peakGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="crashGrad2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#dc2626"/>
    </linearGradient>
  </defs>
  <rect x="10" y="10" width="900" height="360" rx="14" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>

  <!-- lane title -->
  <text x="460" y="40" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="bold" fill="#1e293b">lead = 3 vs lead = 5 &mdash; who captures the peak?</text>

  <!-- ============ LANE: boatlee (lead 3) ============ -->
  <text x="460" y="74" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="13.5" font-weight="bold" fill="#be123c">boatlee (lead 3): sells at step 14</text>
  <polyline points="120,110 230,122 340,140 450,210 560,222 670,222"
            fill="none" stroke="#f472b6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="340" cy="140" r="8" fill="#f43f5e"/>
  <text x="352" y="145" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#be123c">step 14 &middot; mid-price (&asymp;$45)</text>
  <text x="920" y="225" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="11" fill="#b91c1c">crashes after dump</text>

  <!-- ============ LANE: ShiV17 (lead 5) ============ -->
  <text x="460" y="252" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="13.5" font-weight="bold" fill="#047857">ShiV17 (lead 5): sells at step 12</text>
  <polyline points="120,300 230,290 325,272 420,330 670,330"
            fill="none" stroke="url(#peakGrad)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="325" cy="272" r="9" fill="#10b981"/>
  <text x="337" y="277" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="bold" fill="#047857">step 12 &middot; PEAK (&asymp;$100+)</text>

  <!-- boatlee dump marker in lane 2, now at the floor -->
  <circle cx="420" cy="330" r="8" fill="#e11d48" stroke="#ffffff" stroke-width="2"/>
  <text x="432" y="335" font-family="Arial,Helvetica,sans-serif" font-size="12" fill="#991b1b">boatlee's step-14 dump now &rarr; $1</text>

  <!-- crash annotation -->
  <text x="565" y="318" font-family="Arial,Helvetica,sans-serif" font-size="11.5" fill="#b91c1c">ShiV17's dump crashed the market first</text>
  <line x1="420" y1="322" x2="565" y2="322" stroke="#b91c1c" stroke-width="1.2"/>
</svg>
"""

cells.append(md(f"""
<div id="hero" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {EMERALD};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:#047857;font-size:24px;">5 &middot; The Hero &mdash; ShiV17's 5-Turn Counter-Relay</h2>
  <p style="margin:0 0 12px 0;font-size:15px;line-height:1.7;color:{INK};">
    ShiV17 runs the <b>same proven production engine</b> &mdash; but replaces the relay's
    fixed 3-turn lead with a <b>5-turn counter-relay</b>
    (<code style="background:{EMERALD_BG};border:1px solid #a7f3d0;border-radius:5px;padding:1px 6px;">_RC3_RELAY_LEAD = 5</code>,
    triggering at <code style="background:{EMERALD_BG};border:1px solid #a7f3d0;border-radius:5px;padding:1px 6px;">step%24 == 12</code>).
    That two-turn advantage is the entire winning idea:
  </p>
  {svg_contrast}
  <div style="margin-top:12px;display:flex;gap:14px;flex-wrap:wrap;">
    <div style="flex:1;min-width:240px;background:{EMERALD_BG};border:1px solid #a7f3d0;border-radius:10px;padding:12px 16px;color:#064e3b;font-size:14px;line-height:1.6;">
      <b>ShiV17 sells first (step 12)</b> &mdash; thin market, peak price, maximum coins.
    </div>
    <div style="flex:1;min-width:240px;background:{CORAL_BG};border:1px solid #fecdd3;border-radius:10px;padding:12px 16px;color:#881337;font-size:14px;line-height:1.6;">
      <b>boatlee dumps second (step 14)</b> &mdash; into the inventory spike ShiV17 just created, at $1.
    </div>
  </div>
</div>
"""))

# ============================================================================
# 9. HEAD-TO-HEAD RESULTS (charts + tables)
# ============================================================================
cells.append(md(f"""
<div id="results" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {INDIGO};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:{INDIGO};font-size:24px;">6 &middot; Head-to-Head Results</h2>
  <p style="margin:0 0 6px 0;font-size:15px;line-height:1.7;color:{INK};">
    Benchmarks are deterministic head-to-heads on <b>kaggle-environments 1.32.6</b>
    (<code style="background:{INDIGO_SOFT};border:1px solid #c4b5fd;border-radius:5px;padding:1px 6px;">townCenterSellInterval=24</code> "rebalance" regime),
    frozen 8-seed gate family, <b>8 seeds &times; 2 seats = 16 games</b> per opponent.
  </p>
</div>
"""))

code_setup = """
import matplotlib.pyplot as plt
import numpy as np

# ShiV17 color palette (keep it consistent)
INDIGO  = "#6d28d9"
VIOLET  = "#8b5cf6"
EMERALD = "#10b981"
CORAL   = "#f43f5e"
AMBER   = "#f59e0b"
SLATE   = "#64748b"
PAGE    = "#f8fafc"

plt.rcParams.update({
    "figure.facecolor": PAGE,
    "axes.facecolor": PAGE,
    "axes.edgecolor": "#cbd5e1",
    "axes.labelcolor": "#1e293b",
    "text.color": "#1e293b",
    "xtick.color": "#475569",
    "ytick.color": "#475569",
    "font.size": 12,
    "axes.grid": True,
    "grid.color": "#e2e8f0",
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
print("Ship it.")
"""

cells.append(code(code_setup))

code_chart_winrate = """
# ---- Chart 1: win rate, before (V16a) vs after (ShiV17) ----
opponents = ["boatlee V16-RC2", "kaitofukami v27"]
v16a_wr = [0.0, 0.0]                    # 0W / 16L each
shiv17_wr = [93.8, 93.8]                # 15W / 1L each

x = np.arange(len(opponents))
w = 0.34
fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar(x - w/2, v16a_wr, w, label="V16a (before)", color=CORAL, edgecolor="#be123c", linewidth=1)
b2 = ax.bar(x + w/2, shiv17_wr, w, label="ShiV17 (after)", color=EMERALD, edgecolor="#047857", linewidth=1)

for bars in (b1, b2):
    for bar in bars:
        ax.annotate(f"{bar.get_height():.1f}%",
                    (bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha="center", va="bottom", fontsize=12, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(opponents)
ax.set_ylim(0, 110)
ax.set_ylabel("win rate (%)")
ax.set_title("Win rate vs the tape lords: 0% \\u2192 93.8%", fontweight="bold", color=INDIGO, fontsize=15)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
plt.show()
"""

cells.append(code(code_chart_winrate))

code_chart_margins = """
# ---- Chart 2: per-game margin vs boatlee (16 games, 8 seeds x 2 seats) ----
games = ["1M\\u00b70", "1M\\u00b71", "2M\\u00b70", "2M\\u00b71", "3.33M\\u00b70", "3.33M\\u00b71",
         "5M\\u00b70", "5M\\u00b71", "6M\\u00b70", "6M\\u00b71", "7.77M\\u00b70", "7.77M\\u00b71",
         "8M\\u00b70", "8M\\u00b71", "9M\\u00b70", "9M\\u00b71"]
margins = [-1253, 1609] + [176] * 14   # verified per-game deltas (ShiV17 - boatlee)

colors = [EMERALD if m > 0 else CORAL for m in margins]
fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(np.arange(len(margins)), margins, color=colors, edgecolor="#94a3b8", linewidth=0.8)
ax.axhline(0, color="#475569", linewidth=1.1)
ax.set_xticks(np.arange(len(games)))
ax.set_xticklabels(games, rotation=45, ha="right", fontsize=9)
ax.set_ylabel("margin (ShiV17 \\u2212 boatlee)")
ax.set_title("Per-game margins vs boatlee V16-RC2: 15W / 1L (mean \\u0394 +176)", fontweight="bold", color=INDIGO, fontsize=14)

for bar, m in zip(bars, margins):
    ax.annotate(f"{m:+,}", (bar.get_x() + bar.get_width()/2, bar.get_height()),
                ha="center", va="bottom" if m > 0 else "top", fontsize=8.5,
                color="#0f172a", fontweight="bold")
fig.tight_layout()
plt.show()
"""

cells.append(code(code_chart_margins))

code_chart_meandelta = """
# ---- Chart 3: mean delta shift, before vs after ----
opponents = ["vs boatlee V16-RC2", "vs kaitofukami v27"]
v16a_d = [-14735, -13639]
shiv17_d = [176, 3587]

x = np.arange(len(opponents))
w = 0.34
fig, ax = plt.subplots(figsize=(9, 5.2))
b1 = ax.bar(x - w/2, v16a_d, w, label="V16a (before)", color=CORAL, edgecolor="#be123c", linewidth=1)
b2 = ax.bar(x + w/2, shiv17_d, w, label="ShiV17 (after)", color=EMERALD, edgecolor="#047857", linewidth=1)
ax.axhline(0, color="#475569", linewidth=1.1)

for bars in (b1, b2):
    for bar in bars:
        ax.annotate(f"{bar.get_height():+,.0f}",
                    (bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(opponents)
ax.set_ylabel("mean \\u0394 (coins)")
ax.set_title("Mean score delta: from \\u221214,735 to +176 / from \\u221213,639 to +3,587",
             fontweight="bold", color=INDIGO, fontsize=14)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
plt.show()
"""

cells.append(code(code_chart_meandelta))

# --- tables ---
def table_html(title, headers, rows, wins):
    head = "".join(f"<th style='padding:9px 14px;text-align:left;font-size:13px;color:#ffffff;background:{INDIGO};border:1px solid {INDIGO};'>{h}</th>" for h in headers)
    body = ""
    for row, w in zip(rows, wins):
        rowstyle = "background:#d1fae5;" if w else "background:#ffe4e6;"
        cells_html = "".join(
            f"<td style='padding:8px 14px;border:1px solid {BORDER};font-size:13px;{ 'color:#047857;font-weight:800;' if i == 4 else 'color:' + INK + ';'}'>{c}</td>"
            for i, c in enumerate(row)
        )
        body += f"<tr style='{rowstyle}'>" + cells_html + "</tr>"
    return f"""
<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;padding:18px 20px;margin:0 0 16px 0;font-family:Arial,Helvetica,sans-serif;">
  <h3 style="margin:0 0 12px 0;color:{INK};font-size:18px;">{title}</h3>
  <div style="overflow-x:auto;">
  <table style="border-collapse:collapse;width:100%;">
    <thead><tr>{head}</tr></thead>
    <tbody>{body}</tbody>
  </table>
  </div>
  <div style="margin-top:10px;font-size:13px;color:{MUTED};">
    Green rows = ShiV17 win &middot; red rows = ShiV17 loss &middot; margin = ShiV17 score &minus; opponent score.
  </div>
</div>
"""

rows_boatlee = [
    ["1,000,000", "0", "71,363", "72,616", "\\u22121,253", False],
    ["1,000,000", "1", "72,794", "71,185", "+1,609", True],
    ["2,000,000", "0", "81,329", "81,153", "+176", True],
    ["2,000,000", "1", "81,329", "81,153", "+176", True],
    ["3,330,000", "0", "85,883", "85,707", "+176", True],
    ["3,330,000", "1", "85,883", "85,707", "+176", True],
    ["5,000,000", "0", "69,799", "69,623", "+176", True],
    ["5,000,000", "1", "69,799", "69,623", "+176", True],
    ["6,000,000", "0", "41,392", "41,216", "+176", True],
    ["6,000,000", "1", "41,392", "41,216", "+176", True],
    ["7,770,000", "0", "88,937", "88,761", "+176", True],
    ["7,770,000", "1", "88,937", "88,761", "+176", True],
    ["8,000,000", "0", "99,589", "99,413", "+176", True],
    ["8,000,000", "1", "99,589", "99,413", "+176", True],
    ["9,000,000", "0", "110,785", "110,609", "+176", True],
    ["9,000,000", "1", "110,785", "110,609", "+176", True],
]

rows_kaito = [
    ["1,000,000", "0", "71,383", "72,599", "\\u22121,216", False],
    ["1,000,000", "1", "72,814", "71,168", "+1,646", True],
    ["2,000,000", "0", "79,627", "71,697", "+7,930", True],
    ["2,000,000", "1", "79,627", "71,697", "+7,930", True],
    ["3,330,000", "0", "87,104", "77,471", "+9,633", True],
    ["3,330,000", "1", "87,104", "77,471", "+9,633", True],
    ["5,000,000", "0", "69,881", "59,816", "+10,065", True],
    ["5,000,000", "1", "69,881", "59,816", "+10,065", True],
    ["6,000,000", "0", "41,412", "41,199", "+213", True],
    ["6,000,000", "1", "41,412", "41,199", "+213", True],
    ["7,770,000", "0", "88,957", "88,744", "+213", True],
    ["7,770,000", "1", "88,957", "88,744", "+213", True],
    ["8,000,000", "0", "99,609", "99,396", "+213", True],
    ["8,000,000", "1", "99,609", "99,396", "+213", True],
    ["9,000,000", "0", "110,805", "110,592", "+213", True],
    ["9,000,000", "1", "110,805", "110,592", "+213", True],
]

headers = ["Seed", "Seat", "ShiV17", "Opponent", "Margin", "Outcome"]
t1 = table_html("ShiV17 vs boatlee V16-RC2 \\u2014 15W / 1L (93.8%), mean \\u0394 +176",
                headers, [r[:5] + [("WIN" if r[5] else "LOSS")] for r in rows_boatlee],
                [r[5] for r in rows_boatlee])
t2 = table_html("ShiV17 vs kaitofukami v27 \\u2014 15W / 1L (93.8%), mean \\u0394 +3,587",
                headers, [r[:5] + [("WIN" if r[5] else "LOSS")] for r in rows_kaito],
                [r[5] for r in rows_kaito])

cells.append(md(t1))
cells.append(md(t2))

# ============================================================================
# 10. THE IDEA IN 10 LINES
# ============================================================================
cells.append(md(f"""
<div id="idea" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid {VIOLET};border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:{INDIGO};font-size:24px;">7 &middot; The Idea in 10 Lines</h2>
  <p style="margin:0 0 6px 0;font-size:15px;line-height:1.7;color:{INK};">
    The entire winning mechanism, reduced to its essence &mdash; <b>conceptual only</b>,
    not the shipped agent:
  </p>
</div>
"""))

code_idea = """
# The whole winning idea, in 10 lines (conceptual -- not the shipped agent)
RELAY_LEAD = 5                      # sell 5 turns before the scheduled sale, not 3

def should_counter_relay(step):
    # True when our dump lands 2 turns before boatlee's fixed relay
    future_step = step + RELAY_LEAD          # where our sale would land
    return (future_step % 24) == 17          # boatlee's scheduled-sell slot

# Which turns fire? (step 12 with lead 5 -> lands at 17; boatlee dumps at 14)
for step in range(10, 18):
    print(f"step {step:2d} (mod24=={step % 24:2d}): dump={should_counter_relay(step)}")
"""

cells.append(code(code_idea))

# ============================================================================
# 11. LIMITATIONS
# ============================================================================
cells.append(md(f"""
<div id="limits" style="background:{CARD};border:1px solid {BORDER};border-left:6px solid #94a3b8;border-radius:12px;padding:22px 26px;margin:0 0 18px 0;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:#475569;font-size:24px;">8 &middot; What's Not in This Notebook</h2>
  <ul style="margin:0;padding-left:22px;font-size:15px;line-height:1.9;color:{INK};">
    <li><b>No full agent source.</b> The shipped engine (719-step route, relay guard logic, repayment bookkeeping) stays under wraps &mdash; this is a post-mortem, not a giveaway of the ladder-breaking edge.</li>
    <li><b>Narrow but principled evidence.</b> Results are on the frozen 8-seed gate family. The engine is deterministic, so every delta is a real mechanism &mdash; not a coin flip &mdash; but a wider seed sweep is the natural next step.</li>
    <li><b>Meta-dependent.</b> The counter-relay only bites mirror farms that run a fixed-lead relay. Against non-mirror opponents ShiV17 plays as its plain production engine.</li>
    <li><b>Engine version matters.</b> Scoring runs kaggle-environments 1.32.6, which changed the town-demand model mid-competition. Absolute scores are calibrated to that engine.</li>
  </ul>
</div>
"""))

# ============================================================================
# 12. CREDITS
# ============================================================================
cells.append(md(f"""
<div style="background:{HERO_GRAD};border-radius:16px;padding:34px 28px;text-align:center;color:#e0e7ff;font-family:Arial,Helvetica,sans-serif;">
  <h2 style="margin:0 0 10px 0;color:#ffffff;font-size:24px;">ShiV17 &mdash; One Fixed Constant, Front-Run</h2>
  <p style="margin:0 auto 16px auto;max-width:680px;font-size:15px;line-height:1.7;">
    Reverse-engineered the #1 tape, found its hardcoded 3-turn lead, and shipped a
    5-turn counter-relay that beats it 15W/1L. If your opponent always sells three
    turns early, you can sell five turns early &mdash; and reap the peak they were
    planning to steal.
  </p>
  <div style="font-size:12.5px;color:#a5b4fc;letter-spacing:1px;">
    KAGGLECULTURE &middot; AGENT POST-MORTEM &middot; 16 VERIFIED DETERMINISTIC GAMES &middot; KAGGLE-ENVIRONMENTS 1.32.6
  </div>
</div>
"""))

# ============================================================================
# Assemble notebook
# ============================================================================
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0",
            "mimetype": "text/x-python",
            "codemirror_mode": {"name": "ipython", "version": 3},
            "pygments_lexer": "ipython3",
            "nbconvert_exporter": "python",
            "file_extension": ".py",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out_path = r"C:\Users\xxshi\Desktop\farmmasterV2\ShiV17\ShiV17_open_source.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f"Wrote {out_path} with {len(cells)} cells")