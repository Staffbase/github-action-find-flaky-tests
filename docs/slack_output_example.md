# Slack Message Preview

This is how the Slack message renders. Use this for your screenshot.

---

❄️ **Results for failing / flaky tests in [my-app](https://github.com/Staffbase/my-app) (main):**

**Summary window:** `2025-05-26 00:00:00` — `2025-06-01 23:59:59`

---

**Top 6 failed tests (limit=10)**

  80x (100%) `e2e/flows/checkout.spec.ts` [1](https://github.com/Staffbase/my-app/actions/runs/20250601140000) [2](https://github.com/Staffbase/my-app/actions/runs/20250601120000) [3](https://github.com/Staffbase/my-app/actions/runs/20250601100000) [4](https://github.com/Staffbase/my-app/actions/runs/20250601080000) [5](https://github.com/Staffbase/my-app/actions/runs/20250601060000)
  36x (45%) `src/modules/search/search-results.spec.ts` [1](https://github.com/Staffbase/my-app/actions/runs/20250601120000) [2](https://github.com/Staffbase/my-app/actions/runs/20250601100000) [3](https://github.com/Staffbase/my-app/actions/runs/20250601080000) [4](https://github.com/Staffbase/my-app/actions/runs/20250601060000) [5](https://github.com/Staffbase/my-app/actions/runs/20250531220000)
  27x (34%) `src/modules/auth/login.spec.ts` [1](https://github.com/Staffbase/my-app/actions/runs/20250601140000) [2](https://github.com/Staffbase/my-app/actions/runs/20250601100000) [3](https://github.com/Staffbase/my-app/actions/runs/20250601060000) [4](https://github.com/Staffbase/my-app/actions/runs/20250531220000) [5](https://github.com/Staffbase/my-app/actions/runs/20250531020000)
  21x (26%) `src/components/navigation/sidebar.spec.ts` [1](https://github.com/Staffbase/my-app/actions/runs/20250601120000) [2](https://github.com/Staffbase/my-app/actions/runs/20250531080000) [3](https://github.com/Staffbase/my-app/actions/runs/20250531000000) [4](https://github.com/Staffbase/my-app/actions/runs/20250530120000) [5](https://github.com/Staffbase/my-app/actions/runs/20250530100000)
  12x (15%) `src/components/dashboard/widget.spec.tsx` [1](https://github.com/Staffbase/my-app/actions/runs/20250601100000) [2](https://github.com/Staffbase/my-app/actions/runs/20250530140000) [3](https://github.com/Staffbase/my-app/actions/runs/20250530060000) [4](https://github.com/Staffbase/my-app/actions/runs/20250528220000) [5](https://github.com/Staffbase/my-app/actions/runs/20250528060000)
  2x (2%) `src/modules/settings/profile.spec.tsx` [1](https://github.com/Staffbase/my-app/actions/runs/20250601020000) [2](https://github.com/Staffbase/my-app/actions/runs/20250530220000)

---

**🔄 Top 6 flaky tests — green → red flips (limit=10)**

  25% flaky (20 flips / 80 runs) `src/modules/auth/login.spec.ts`
  🟩🟨🟨🟨🟩🟨🟨🟨🟩🟨🟨🟨🟥🟨🟨🟨🟨🟨🟩🟨🟨🟩🟨🟨🟩🟩🟨🟩🟨🟨 _(80 runs)_

  24% flaky (19 flips / 80 runs) `src/modules/search/search-results.spec.ts`
  🟥🟨🟨🟥🟨🟨🟩🟩🟨🟩🟨🟨🟨🟨🟥🟨🟨🟨🟨🟥🟩🟨🟨🟨🟩🟨🟨🟩🟨🟨 _(80 runs)_

  19% flaky (15 flips / 80 runs) `src/components/navigation/sidebar.spec.ts`
  🟨🟨🟩🟨🟩🟨🟨🟨🟨🟨🟨🟨🟨🟩🟩🟩🟨🟨🟨🟩🟨🟩🟨🟩🟨🟩🟩🟩🟩🟨 _(80 runs)_

  10% flaky (8 flips / 80 runs) `src/components/dashboard/widget.spec.tsx`
  🟨🟩🟨🟥🟩🟩🟩🟩🟨🟨🟨🟩🟩🟨🟩🟩🟩🟩🟩🟨🟨🟩🟩🟩🟩🟩🟩🟩🟩🟨 _(80 runs)_

  1% flaky (1 flips / 80 runs) `src/modules/settings/profile.spec.tsx`
  🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟨🟩🟩🟩🟩🟨🟩🟩 _(80 runs)_

  0% flaky (0 flips / 80 runs) `e2e/flows/checkout.spec.ts`
  🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 _(80 runs)_

> **Legend:** 🟩 = mostly pass · 🟥 = mostly fail · 🟨 = mixed (oldest → newest)

---

### Raw Slack JSON payload

```json
{
    "channel": "C12345678",
    "text": "Flaky Tests Summary",
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":snowflake: Results for failing / flaky tests in <https://github.com/Staffbase/my-app|my-app> (main):"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Summary window: 2025-05-26 00:00:00 - 2025-06-01 23:59:59"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Top 6 failed tests (limit=10)\n80x (100%) `e2e/flows/checkout.spec.ts` <https://github.com/Staffbase/my-app/actions/runs/20250601140000|1> <https://github.com/Staffbase/my-app/actions/runs/20250601120000|2> <https://github.com/Staffbase/my-app/actions/runs/20250601100000|3> <https://github.com/Staffbase/my-app/actions/runs/20250601080000|4> <https://github.com/Staffbase/my-app/actions/runs/20250601060000|5>\n36x (45%) `src/modules/search/search-results.spec.ts` <https://github.com/Staffbase/my-app/actions/runs/20250601120000|1> <https://github.com/Staffbase/my-app/actions/runs/20250601100000|2> <https://github.com/Staffbase/my-app/actions/runs/20250601080000|3> <https://github.com/Staffbase/my-app/actions/runs/20250601060000|4> <https://github.com/Staffbase/my-app/actions/runs/20250531220000|5>\n27x (34%) `src/modules/auth/login.spec.ts` <https://github.com/Staffbase/my-app/actions/runs/20250601140000|1> <https://github.com/Staffbase/my-app/actions/runs/20250601100000|2> <https://github.com/Staffbase/my-app/actions/runs/20250601060000|3> <https://github.com/Staffbase/my-app/actions/runs/20250531220000|4> <https://github.com/Staffbase/my-app/actions/runs/20250531020000|5>\n21x (26%) `src/components/navigation/sidebar.spec.ts` <https://github.com/Staffbase/my-app/actions/runs/20250601120000|1> <https://github.com/Staffbase/my-app/actions/runs/20250531080000|2> <https://github.com/Staffbase/my-app/actions/runs/20250531000000|3> <https://github.com/Staffbase/my-app/actions/runs/20250530120000|4> <https://github.com/Staffbase/my-app/actions/runs/20250530100000|5>\n12x (15%) `src/components/dashboard/widget.spec.tsx` <https://github.com/Staffbase/my-app/actions/runs/20250601100000|1> <https://github.com/Staffbase/my-app/actions/runs/20250530140000|2> <https://github.com/Staffbase/my-app/actions/runs/20250530060000|3> <https://github.com/Staffbase/my-app/actions/runs/20250528220000|4> <https://github.com/Staffbase/my-app/actions/runs/20250528060000|5>\n"
            },
            "expand": true
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Top 6 failed tests (limit=10) (cont.)\n2x (2%) `src/modules/settings/profile.spec.tsx` <https://github.com/Staffbase/my-app/actions/runs/20250601020000|1> <https://github.com/Staffbase/my-app/actions/runs/20250530220000|2>\n"
            },
            "expand": true
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":arrows_counterclockwise: Top 6 flaky tests \u2014 green \u2192 red flips (limit=10)\n25% flaky (20 flips / 80 runs) `src/modules/auth/login.spec.ts`\n    \ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe5\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8 _(80 runs)_\n24% flaky (19 flips / 80 runs) `src/modules/search/search-results.spec.ts`\n    \ud83d\udfe5\ud83d\udfe8\ud83d\udfe8\ud83d\udfe5\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe5\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe5\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8 _(80 runs)_\n19% flaky (15 flips / 80 runs) `src/components/navigation/sidebar.spec.ts`\n    \ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8 _(80 runs)_\n10% flaky (8 flips / 80 runs) `src/components/dashboard/widget.spec.tsx`\n    \ud83d\udfe8\ud83d\udfe9\ud83d\udfe8\ud83d\udfe5\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8 _(80 runs)_\n1% flaky (1 flips / 80 runs) `src/modules/settings/profile.spec.tsx`\n    \ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe9\ud83d\udfe8\ud83d\udfe9\ud83d\udfe9 _(80 runs)_\n"
            },
            "expand": true
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":arrows_counterclockwise: Top 6 flaky tests \u2014 green \u2192 red flips (limit=10) (cont.)\n0% flaky (0 flips / 80 runs) `e2e/flows/checkout.spec.ts`\n    \ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5\ud83d\udfe5 _(80 runs)_\n"
            },
            "expand": true
        }
    ]
}
```