# Alpha Qwixx: Strategy Lessons from the RL Agent

*Extracted from a PPO self-play model trained over 500k+ episodes, achieving 89.6% win rate vs Hard AI (85.6% over 500-game eval).*

---

## 1. Almost Never Skip

The agent's #1 lesson is brutally simple: **take a number whenever you can.** Across every scenario tested, the skip action almost never exceeds 1% probability. Even in awkward situations — bad white sums, big gaps — the agent would rather mark *something* than pass.

The one exception: when 2 strong rows are already built and the only option is starting a 3rd color with a middling number, the agent considers skipping (~17%). But even then, it leans toward marking.

**Takeaway: If you're debating "should I take this?" — the answer is almost always yes.**

---

## 2. Build Dense Rows (But Don't Be Afraid of Small Gaps)

When a number is the perfect next sequential mark, the agent takes it with 69-99% confidence. A gap of 1 number? Still takes it eagerly (91%). A gap of 5 numbers? It gets much less enthusiastic about that specific row (30%) and starts looking at other colors instead.

| Scenario | Confidence |
|----------|-----------|
| Red 2-6, take 7 (perfect) | 69% |
| Red 2,3,4, take 6 (gap of 1) | 91% |
| Red 2 only, take 8 (gap of 5) | 30% (looks elsewhere) |

**Takeaway: Gaps of 1-2 are fine. Gaps of 5+ mean you should check other colors first.**

---

## 3. Red Is the Favorite Color

When all rows are empty and any color is equally available, the agent consistently prefers **Red at ~59%**, followed by Blue (~15%), Green (~13%), and Yellow (~12%). This isn't random — the agent has discovered that Red (ascending 2-12) has strategic advantages, possibly because:

- Low numbers (2-4) come up most frequently with two white dice
- Building Red from the bottom is the most natural path to a lock
- Red is listed/processed first — a minor neural net positional bias is also possible

**Takeaway: When in doubt, invest in Red first, then Blue/Green.**

---

## 4. Low Numbers Go to Red/Yellow, High Numbers Go to Green/Blue

The agent has deeply internalized the ascending vs descending row structure:

- **White sum 3** → Red 64%, Yellow 36% (ascending rows start low)
- **White sum 11** → Green 85%, Blue 15% (descending rows start high)
- **White sum 7** → Red 59% (middle ground, still favors Red)

**Takeaway: This seems obvious, but the agent is emphatic about it. Don't put low numbers in Green/Blue or high numbers in Red/Yellow — the probability drops to <1%.**

---

## 5. Always Lock If You Can

When the agent can lock a row (has 5+ marks and can reach the lock number), it takes it with ~75% confidence — and the remaining 25% is considering locking a *different* color, not skipping.

The interesting part: **the agent will lock even if it means skipping 3 numbers** (Red 2-8, skip 9,10,11, mark 12 to lock = 76% confidence). The lock bonus is worth the skipped numbers.

**Takeaway: If you can lock a row, do it. The 12-point lock bonus is massive.**

---

## 6. Stage 2: Go Low (Ascending Rows) or Sequential

In Stage 2 (white + colored die), the agent strongly prefers the **lower available number** in ascending rows. With Red-5 vs Red-6 available, it picks Red-5 at 81%.

This makes sense — taking the lower number preserves optionality for future turns. Taking 6 first means 5 is dead forever.

**Takeaway: In Stage 2, take the smaller number in Red/Yellow and the larger number in Green/Blue when you have options.**

---

## 7. Focus Over Spread

When the agent has Red 2,3,4 and white sum is 5, it extends Red with **99% confidence** rather than starting Yellow-5. It has learned that deep rows are exponentially more valuable than wide-but-shallow coverage (Qwixx scoring: 1,3,6,10,15,21,28,36,45,55,66,78).

However, once two rows are well-established, it *will* diversify — but even then it's cautious (48% Blue, 35% Green, 17% skip vs starting a 3rd row).

**Takeaway: Get one or two rows deep before spreading. A single row with 8 marks (36 points) crushes four rows with 2 marks each (4 points).**

---

## 8. Avoid Jumping in Your Own Row, But Jump in Untouched Rows

When Red has marks at 2,3 and white sum is 10, the agent avoids Red-10 (0.8%) because it would kill numbers 4-9. Instead it pivots to Blue-10 (73%) or Green-10 (26%) where 10 is a *starting* position, not a jump.

**Takeaway: Big jumps in a row you've already started are terrible. The same number in a fresh row (or a descending row where it's early) is great.**

---

## 9. The Agent Knows When It's Losing

The value function reveals the agent's self-assessment:

| Position | Value |
|----------|-------|
| Two strong rows built | +4.49 |
| One row ahead of opponent | +3.87 |
| Even position | +3.47 |
| 3 penalties (desperate) | +2.98 |
| Empty board | +2.66 |
| Opponent has Red 2-8, we have nothing | +1.27 |

When behind, the agent gets **more aggressive** — skip probability drops even lower and it takes riskier marks. When ahead, it's slightly more selective.

**Takeaway: If you're behind, take everything. If you're ahead, you can afford to be slightly pickier.**

---

## 10. Game Replay Insights

Watching the agent play a full game reveals its tempo:

- **Turns 0-2**: Rapidly builds Red (5, 6, 8) and starts Blue (6) and Green (11) simultaneously
- **Turns 5-10**: Fills in Yellow (5, 6, 8, 9) while extending Green (10, 9, 6, 5) — building two secondary rows
- **Turn 11**: One of the *rare* skips — white sum 3 with no good options
- **Turns 14-20**: Opportunistic late marks to pad score

The agent averages **55.1 points** vs Hard AI's typical ~40. It does this by marking efficiently across 3-4 colors rather than tunnel-visioning one row.

---

## Summary: The Alpha Qwixx Playbook

1. **Mark something on almost every turn** — skipping is almost never correct
2. **Start with Red** (or Green/Blue for high white sums)
3. **Build one row deep before spreading** — depth beats breadth
4. **Take the lower number when you have options** in ascending rows
5. **Small gaps (1-2) are fine, large gaps (5+) mean try another color**
6. **Always lock a row if you can**, even if it means skipping numbers
7. **Never jump in a row you've already started** — use fresh rows for outlier numbers
8. **When behind, get more aggressive** — take riskier marks
9. **In Stage 2, favor extending existing rows** over starting new ones
10. **Aim for 3 solid rows** as your end-game target
