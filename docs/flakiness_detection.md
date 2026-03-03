# Flakiness Detection: How It Works

## Overview

This script distinguishes between **consistently failing tests** and **truly flaky tests** by analyzing the sequence of pass/fail results over time.

## Method: Fail-After-Pass Detection

The script uses **fail-after-pass transition counting** to measure flakiness.

A "flip" is defined as: a test that **was passing** in a previous run and then **fails again** in a later run — within the same CI check name (e.g. `ci-unit`).

### Algorithm

For each CI check name (e.g. `ci-unit`, `ci-e2e`), the script:

1. Sorts all runs chronologically
2. Tracks the **last known status** (pass or fail) for every test file
3. When a test transitions from **pass → fail**, it records a **flip event**
4. Counts the total number of flips per test

The **flakiness rate** is then:

```
flakiness_rate = number_of_flips / total_runs
```

### Example

Given 7 runs of `ci-unit` for two tests:

```
Run   login.spec.ts   checkout.spec.ts
─────────────────────────────────────────
 1    ❌ fail          ❌ fail
 2    ✅ pass          ❌ fail
 3    ❌ fail ← flip   ❌ fail
 4    ❌ fail          ❌ fail
 5    ✅ pass          ❌ fail
 6    ❌ fail ← flip   ❌ fail
 7    ✅ pass          ❌ fail
```

| Metric                 | `login.spec.ts` | `checkout.spec.ts` |
|------------------------|:---------------:|:------------------:|
| Failures               | 4 / 7           | 7 / 7              |
| Failure rate           | 57%             | 100%               |
| Pass → Fail flips      | 2               | 0                  |
| **Flakiness rate**     | **29%**         | **0%**             |

- `checkout.spec.ts` fails every single time — high failure rate, but **0% flaky** because it never passes, so it can never flip back to red. It's **consistently broken**.
- `login.spec.ts` alternates between pass and fail — lower failure rate, but **29% flaky** because it keeps flipping. This is the **classic flaky test pattern**.

## What This Detects

✅ Tests that **alternate between green and red** across CI runs — the classic flaky pattern  
✅ Tests that **fail intermittently** on the same branch with no code changes  
✅ Differences between "broken" (always red) and "unreliable" (sometimes red)

## What This Does Not Detect

❌ Flakiness **within a single run** (e.g. a test passes on retry inside the same CI job)  
❌ **Order-dependent** flakiness (test A causes test B to fail)  
❌ **Environment-dependent** flakiness (works on one runner type, fails on another)  
❌ **Timing-sensitive** flakiness that only manifests under load

## Output

The script produces two ranked lists:

| List              | Ranked by              | Purpose                                    |
|-------------------|------------------------|--------------------------------------------|
| **Most failing**  | Total failure count    | Find tests that are broken the most        |
| **Most flaky**    | Fail-after-pass rate   | Find tests that flip between green and red  |

Each flaky test includes a **visual timeline stripe** showing its pass/fail history:

```
29% flaky · 2 flips / 7 runs · login.spec.ts
🟥🟩🟥🟥🟩🟥🟩
```

When there are more than 30 data points, runs are **bucketed** into 30 columns. Each column shows the dominant result of its group:

- 🟩 = mostly passing (≤30% failures in bucket)
- 🟥 = mostly failing (≥70% failures in bucket)
- 🟨 = mixed results (30–70% failures in bucket)

