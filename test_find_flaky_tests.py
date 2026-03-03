"""Unit tests for compute_test_stats and ranking helpers."""
from datetime import datetime, timedelta
from find_flaky_tests import (
    CommitDigest,
    FlipEvent,
    Occurrence,
    RunInfo,
    RunResult,
    FileStats,
    MAX_TIMELINE_WIDTH,
    _bucket_timeline,
    compute_test_stats,
    top_most_failing,
    top_most_flaky,
    format_failing_item,
    format_flaky_item,
    print_summary_for_humans,
    render_timeline_human,
    render_timeline_slack,
)


def _digest(sha: str, ts: str = "2025-06-01T10:00:00Z") -> CommitDigest:
    return CommitDigest(sha=sha, timestamp=datetime.fromisoformat(ts.replace("Z", "+00:00")))


def _occ(sha: str, path: str, url: str = "https://example.com/check/1") -> Occurrence:
    return Occurrence(commit=_digest(sha), check_url=url, annotation_path=path)


def _run(name: str, ts: str, failed: tuple[str, ...] = (), url: str = "https://example.com/check/1") -> RunInfo:
    return RunInfo(
        name=name,
        timestamp=datetime.fromisoformat(ts.replace("Z", "+00:00")),
        check_url=url,
        failed_paths=failed,
    )


# ── Scenario: a consistently failing test vs a flaky test ──────────────────────
# TestA fails every run   → high fail count, 0 fail-after-pass (never passes)
# TestB fails, passes, fails → lower fail count, but has fail-after-pass transitions
def make_scenario():
    runs = [
        # check "ci" run 1: TestA fails, TestB fails
        _run("ci", "2025-06-01T01:00:00Z", ("TestA.spec.ts", "TestB.spec.ts")),
        # check "ci" run 2: TestA fails, TestB passes
        _run("ci", "2025-06-01T02:00:00Z", ("TestA.spec.ts",)),
        # check "ci" run 3: TestA fails, TestB fails again (fail-after-pass!)
        _run("ci", "2025-06-01T03:00:00Z", ("TestA.spec.ts", "TestB.spec.ts")),
        # check "ci" run 4: TestA fails, TestB passes
        _run("ci", "2025-06-01T04:00:00Z", ("TestA.spec.ts",)),
        # check "ci" run 5: TestA fails, TestB fails again (another fail-after-pass)
        _run("ci", "2025-06-01T05:00:00Z", ("TestA.spec.ts", "TestB.spec.ts")),
    ]
    occurrences = []
    for i, r in enumerate(runs):
        for p in r.failed_paths:
            occurrences.append(_occ(f"sha{i}", p, r.check_url))
    return occurrences, runs


def test_compute_test_stats_counts():
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)

    by_path = {s.path: s for s in stats}
    assert "TestA.spec.ts" in by_path
    assert "TestB.spec.ts" in by_path

    a = by_path["TestA.spec.ts"]
    b = by_path["TestB.spec.ts"]

    # TestA fails in all 5 runs
    assert a.fail_count == 5
    assert a.total_runs == 5
    assert a.fail_rate == 1.0
    # TestA never passes then fails again – it fails from the start and keeps failing
    assert a.fail_after_pass == 0

    # TestB fails in 3 of 5 runs
    assert b.fail_count == 3
    assert b.total_runs == 5
    assert b.fail_rate == 3 / 5
    # TestB has 2 fail-after-pass transitions (run3 and run5)
    assert b.fail_after_pass == 2
    assert b.fail_after_pass_rate == 2 / 5

    # TestA has no flips → no flip events
    assert a.flip_events == []

    # TestB has 2 flip events with correct timestamps
    assert len(b.flip_events) == 2
    # First flip: passed at run2 (02:00), failed at run3 (03:00)
    assert b.flip_events[0].check_name == "ci"
    assert b.flip_events[0].passed_at.hour == 2
    assert b.flip_events[0].failed_at.hour == 3
    # Second flip: passed at run4 (04:00), failed at run5 (05:00)
    assert b.flip_events[1].passed_at.hour == 4
    assert b.flip_events[1].failed_at.hour == 5


def test_top_most_failing_ranks_by_count():
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)
    top = top_most_failing(stats, 12)

    # TestA (5 failures) should be ranked above TestB (3 failures)
    assert top[0].path == "TestA.spec.ts"
    assert top[1].path == "TestB.spec.ts"


def test_top_most_flaky_ranks_by_fail_after_pass():
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)
    top = top_most_flaky(stats, 12)

    # TestB (40% fail-after-pass) should be ranked above TestA (0% fail-after-pass)
    assert top[0].path == "TestB.spec.ts"
    assert top[1].path == "TestA.spec.ts"


def test_format_failing_item():
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)
    by_path = {s.path: s for s in stats}
    result = format_failing_item(by_path["TestA.spec.ts"])
    assert "*5x*" in result
    assert "100%" in result
    assert "TestA.spec.ts" in result


def test_format_flaky_item():
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)
    by_path = {s.path: s for s in stats}
    result = format_flaky_item(by_path["TestB.spec.ts"])
    assert "*40%*" in result
    assert "2 flips / 5 runs" in result
    assert "·" in result  # dot separators
    assert "TestB.spec.ts" in result
    # Should contain compact Slack timeline square emoji
    assert "🟥" in result
    assert "🟩" in result


def test_print_summary_for_humans(capsys):
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)
    print_summary_for_humans(stats)
    captured = capsys.readouterr().out
    assert "Most failing tests" in captured
    assert "Most flaky tests" in captured
    assert "green → red" in captured
    assert "TestA.spec.ts" in captured
    assert "TestB.spec.ts" in captured
    # Timeline stripes should use ▅ block characters
    assert "▅" in captured


def test_render_timeline_human():
    tl = [
        RunResult(datetime(2025, 6, 1, 1), "u1", "ci", True),
        RunResult(datetime(2025, 6, 1, 2), "u2", "ci", False),
        RunResult(datetime(2025, 6, 1, 3), "u3", "ci", True),
        RunResult(datetime(2025, 6, 1, 4), "u4", "ci", False),
        RunResult(datetime(2025, 6, 1, 5), "u5", "ci", False),
    ]
    result = render_timeline_human(tl)
    # Should contain 5 ▅ block characters with ANSI color codes
    assert result.count("▅") == 5
    assert "\033[91m" in result  # red ANSI
    assert "\033[92m" in result  # green ANSI


def test_render_timeline_slack():
    tl = [
        RunResult(datetime(2025, 6, 1, 1), "u1", "ci", True),
        RunResult(datetime(2025, 6, 1, 2), "u2", "ci", False),
        RunResult(datetime(2025, 6, 1, 3), "u3", "ci", True),
    ]
    result = render_timeline_slack(tl)
    assert result == "🟥🟩🟥"


def test_render_timeline_empty():
    assert render_timeline_human([]) == ""
    assert render_timeline_slack([]) == ""


def test_run_timeline_in_stats():
    """Verify that run_timeline is populated correctly in FileStats."""
    occurrences, runs = make_scenario()
    stats = compute_test_stats(occurrences, runs)
    by_path = {s.path: s for s in stats}

    # TestA fails every run → all red
    a_tl = by_path["TestA.spec.ts"].run_timeline
    assert len(a_tl) == 5
    assert all(r.failed for r in a_tl)
    a_rendered = render_timeline_human(a_tl)
    assert a_rendered.count("▅") == 5
    assert "\033[92m" not in a_rendered  # no green

    # TestB: fail, pass, fail, pass, fail → alternating
    b_tl = by_path["TestB.spec.ts"].run_timeline
    assert len(b_tl) == 5
    expected = [True, False, True, False, True]
    assert [r.failed for r in b_tl] == expected
    b_rendered = render_timeline_human(b_tl)
    assert b_rendered.count("▅") == 5
    assert "\033[91m" in b_rendered  # has red
    assert "\033[92m" in b_rendered  # has green


def test_empty_runs():
    stats = compute_test_stats([], [])
    assert stats == []
    assert top_most_failing(stats, 12) == []
    assert top_most_flaky(stats, 12) == []


def test_multiple_check_names():
    """Tests that run across different check names are handled correctly."""
    runs = [
        _run("lint", "2025-06-01T01:00:00Z", ("TestC.spec.ts",)),
        _run("lint", "2025-06-01T02:00:00Z", ()),  # passes
        _run("lint", "2025-06-01T03:00:00Z", ("TestC.spec.ts",)),  # fail-after-pass
        _run("unit", "2025-06-01T01:00:00Z", ("TestC.spec.ts",)),
        _run("unit", "2025-06-01T02:00:00Z", ()),  # passes
        _run("unit", "2025-06-01T03:00:00Z", ()),  # stays passing
    ]
    occurrences = []
    for i, r in enumerate(runs):
        for p in r.failed_paths:
            occurrences.append(_occ(f"sha{i}", p, r.check_url))

    stats = compute_test_stats(occurrences, runs)
    assert len(stats) == 1
    c = stats[0]
    assert c.path == "TestC.spec.ts"
    # fails in 3 runs total (lint:2 + unit:1), total_runs = lint:3 + unit:3 = 6
    assert c.fail_count == 3
    assert c.total_runs == 6
    # fail-after-pass: 1 in lint, 0 in unit = 1
    assert c.fail_after_pass == 1
    assert c.fail_after_pass_rate == 1 / 6
    # flip event comes from the "lint" check
    assert len(c.flip_events) == 1
    assert c.flip_events[0].check_name == "lint"
    assert c.flip_events[0].passed_at.hour == 2
    assert c.flip_events[0].failed_at.hour == 3


def test_flip_events_record_correct_urls():
    """Flip events should record the URLs of the passing and failing runs."""
    runs = [
        _run("ci", "2025-06-01T01:00:00Z", ("Flaky.spec.ts",), url="https://example.com/run/1"),
        _run("ci", "2025-06-01T02:00:00Z", (),                  url="https://example.com/run/2"),  # pass
        _run("ci", "2025-06-01T03:00:00Z", ("Flaky.spec.ts",),  url="https://example.com/run/3"),  # flip!
    ]
    occurrences = []
    for i, r in enumerate(runs):
        for p in r.failed_paths:
            occurrences.append(_occ(f"sha{i}", p, r.check_url))

    stats = compute_test_stats(occurrences, runs)
    assert len(stats) == 1
    s = stats[0]
    assert len(s.flip_events) == 1
    flip = s.flip_events[0]
    assert flip.test_path == "Flaky.spec.ts"
    assert flip.check_name == "ci"
    assert flip.passed_url == "https://example.com/run/2"
    assert flip.failed_url == "https://example.com/run/3"


def test_bucket_timeline_small():
    """When runs fit within max_width, each run is its own bucket."""
    tl = [
        RunResult(datetime(2025, 6, 1, i), "", "ci", i % 2 == 0)
        for i in range(5)
    ]
    buckets = _bucket_timeline(tl, 30)
    assert len(buckets) == 5
    assert buckets == [1.0, 0.0, 1.0, 0.0, 1.0]


def test_bucket_timeline_large():
    """When runs exceed max_width, they are grouped into buckets."""
    # 90 runs, all failing → 30 buckets, each 1.0
    base = datetime(2025, 6, 1)
    tl = [
        RunResult(base + timedelta(minutes=i), "", "ci", True)
        for i in range(90)
    ]
    buckets = _bucket_timeline(tl, 30)
    assert len(buckets) == 30
    assert all(b == 1.0 for b in buckets)


def test_bucket_timeline_mixed_large():
    """Buckets with a mix of pass/fail show intermediate ratios."""
    # 60 runs: first 30 fail, last 30 pass → bucket into 30 columns
    base = datetime(2025, 6, 1)
    tl = [
        RunResult(base + timedelta(minutes=i), "", "ci", i < 30)
        for i in range(60)
    ]
    buckets = _bucket_timeline(tl, 30)
    assert len(buckets) == 30
    # First 15 buckets should be 1.0 (all fail), last 15 should be 0.0 (all pass)
    assert all(b == 1.0 for b in buckets[:15])
    assert all(b == 0.0 for b in buckets[15:])


def test_render_timeline_human_bucketed():
    """When timeline exceeds MAX_TIMELINE_WIDTH, output is bucketed and shows run count."""
    base = datetime(2025, 6, 1)
    tl = [
        RunResult(base + timedelta(minutes=i), "", "ci", i % 3 == 0)
        for i in range(60)
    ]
    result = render_timeline_human(tl)
    # Should be capped at MAX_TIMELINE_WIDTH columns
    assert result.count("▅") == MAX_TIMELINE_WIDTH
    # Should show total run count
    assert "(60 runs)" in result


def test_render_timeline_slack_bucketed():
    """When timeline exceeds MAX_TIMELINE_WIDTH, Slack output is bucketed and shows run count."""
    base = datetime(2025, 6, 1)
    tl = [
        RunResult(base + timedelta(minutes=i), "", "ci", i % 3 == 0)
        for i in range(60)
    ]
    result = render_timeline_slack(tl)
    # Count emoji characters (🟥, 🟩, 🟨)
    emoji_count = sum(1 for c in result if c in "🟥🟩🟨")
    assert emoji_count == MAX_TIMELINE_WIDTH
    # Should show total run count
    assert "(60 runs)" in result


def test_render_timeline_slack_no_label_when_small():
    """When timeline fits within MAX_TIMELINE_WIDTH, no run count label is added."""
    tl = [
        RunResult(datetime(2025, 6, 1, i), "", "ci", False)
        for i in range(5)
    ]
    result = render_timeline_slack(tl)
    assert "runs)" not in result
    assert result == "🟩🟩🟩🟩🟩"


def test_render_timeline_slack_yellow_mixed():
    """Buckets with ~50/50 pass/fail should show yellow 🟨."""
    # 60 runs alternating fail/pass → each 2-run bucket has 1 fail + 1 pass = 0.5 ratio → yellow
    base = datetime(2025, 6, 1)
    tl = [
        RunResult(base + timedelta(minutes=i), "", "ci", i % 2 == 0)
        for i in range(60)
    ]
    result = render_timeline_slack(tl)
    assert "🟨" in result


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
















