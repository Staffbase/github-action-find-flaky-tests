import argparse
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from github import Auth, Repository
from github import Github
from typing import Dict, List
import json as json_lib

MAX_FILENAME_LENGTH = 60
TOP_LIMIT = 10
MAX_TIMELINE_WIDTH = 30  # max columns in timeline stripe


@dataclass
class CommitDigest:
    sha: str
    timestamp: datetime


@dataclass
class Occurrence:
    commit: CommitDigest
    check_url: str
    annotation_path: str


@dataclass
class RunInfo:
    name: str
    timestamp: datetime
    check_url: str
    failed_paths: tuple[str, ...]


@dataclass
class FlipEvent:
    """Records a single green → red transition for a test."""
    test_path: str
    check_name: str
    passed_at: datetime        # timestamp of the last passing run
    passed_url: str            # check URL of the last passing run
    failed_at: datetime        # timestamp of the run that flipped to red
    failed_url: str            # check URL of the run that flipped to red


@dataclass
class RunResult:
    """A single run result for a specific test (used for timeline rendering)."""
    timestamp: datetime
    check_url: str
    check_name: str
    failed: bool


@dataclass
class FileStats:
    path: str
    fail_count: int
    total_runs: int
    fail_rate: float
    fail_after_pass: int
    fail_after_pass_rate: float
    recent_occurrences: List[Occurrence]
    flip_events: List[FlipEvent]
    run_timeline: List[RunResult]


@dataclass
class AppState:
    auth_token: str
    org: str
    repo: str
    branch: str
    slack_channel: str | None
    path_suffixes: tuple[str, ...] | None
    prefix: str | None
    since: datetime | None
    until: datetime | None


def parse_since(s: str | None) -> datetime:
    if s is None:
        return datetime.now() - timedelta(days=7)
    return parse_datetime(s)


def parse_until(s: str | None) -> datetime:
    if s is None:
        return datetime.now()
    return parse_datetime(s)


def parse_datetime(s):
    if 'T' in s:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    else:
        return datetime.strptime(s, '%Y-%m-%d')

# parse_suffixes_tuple is used to parse the suffixes argument from CLI
# example: ".spec.ts,.spec.tsx,.test.ts,test.tsx" -> ('.spec.ts', '.spec.tsx', '.test.ts', 'test.tsx')
def parse_suffixes_tuple(s: str | None) -> tuple[str, ...] | None:
    if s is None:
        return None
    else:
        return tuple(item.strip() for item in s.split(','))


def validate_and_split_repo(repo: str) -> tuple[str, str]:
    if '/' not in repo:
        raise ValueError(f"Invalid repo format: {repo}")
    org, repo = repo.split('/')
    return org, repo


def parse_args() -> AppState:
    """Parse CLI arguments. Exit if invalid or help requested."""
    parser = argparse.ArgumentParser(description='Find all occurrences of annotations in a GitHub repo.', add_help=True,
                                     exit_on_error=True)
    parser.add_argument('--auth-token', type=str, help='GitHub auth token (required)', required=True)
    parser.add_argument('--slack-channel', type=str,
                        help='Format output for posting in Slack to given channel')
    parser.add_argument('--path-suffixes', type=str, help='file path suffixes to filter annotations by. Could be tuple ".spec.ts,.spec.tsx,.test.ts,.test.tsx"',)
    parser.add_argument('--prefix', type=str, help='prefix to filter annotations by', required=True)
    parser.add_argument('--since', type=str,
                        help='date to start from, format YYYY-MM-DD defaults to start of day (midnight UTC), '
                             'format YYYY-MM-DDTHH:MM:SSZ is also supported. Defaults to start of day one week ago.')
    parser.add_argument('--until', type=str,
                        help='date to end at, format YYYY-MM-DD defaults to end of day (midnight of next day UTC), '
                             'format YYYY-MM-DDTHH:MM:SSZ is also supported. Defaults to now.')
    parser.add_argument("repo", metavar="repo", type=str,
                        help="GitHub repo to search in, format <org>/<repo> (required)")
    parser.add_argument("branch", metavar="branch", type=str, help="git branch to check (defaults to 'main')",
                        default="main")
    args = parser.parse_args()
    try:
        (org, repo) = validate_and_split_repo(args.repo)
        return AppState(
            auth_token=args.auth_token,
            org=org,
            repo=repo,
            branch=args.branch,
            since=parse_since(args.since),
            until=parse_until(args.until),
            slack_channel=args.slack_channel,
            path_suffixes=parse_suffixes_tuple(args.path_suffixes),
            prefix=args.prefix
        )
    except Exception as e:
        print(f"Error: {e}")
        parser.print_help()
        exit(1)


def print_for_humans(occurrences: List[Occurrence], stats: List[FileStats]):
    print_summary_for_humans(stats)
    print("")
    print("All matching occurrences:")
    occurrences_by_ann_path: Dict[str, List[Occurrence]] = {}
    for o in occurrences:
        occurrences_by_ann_path.setdefault(o.annotation_path, []).append(o)
    for ann_path, occrs in occurrences_by_ann_path.items():
        print(f"{ann_path}:")
        for o in occrs:
            print(f"    in {o.commit.sha} on {o.commit.timestamp}, see {o.check_url}")


def print_summary_for_humans(stats: List[FileStats]):
    most_failing = top_most_failing(stats, TOP_LIMIT)
    most_flaky = top_most_flaky(stats, TOP_LIMIT)

    print(f"Most failing tests (top {len(most_failing)}, limit={TOP_LIMIT}):")
    for s in most_failing:
        print(f"  {s.fail_count}x ({s.fail_rate:.0%}) {s.path}")

    print("")
    print(f"Most flaky tests (top {len(most_flaky)}, limit={TOP_LIMIT}):")
    print(f"  Ranked by fail-after-pass rate: how often a test flips from green → red.")
    print(f"  Timeline: oldest → newest (\033[92m▅\033[0m pass, \033[91m▅\033[0m fail, \033[93m▅\033[0m mixed)"
          f" — max {MAX_TIMELINE_WIDTH} columns, grouped if more runs")
    print("")
    for s in most_flaky:
        timeline = render_timeline_human(s.run_timeline)
        print(
            f"  {s.fail_after_pass_rate:.0%} flaky ({s.fail_after_pass} flips / {s.total_runs} runs) "
            f"{s.path}"
        )
        print(f"    {timeline}")



def _bucket_timeline(timeline: List[RunResult], max_width: int) -> List[float]:
    """Group timeline into max_width buckets, each returning a fail ratio (0.0–1.0).

    If timeline fits within max_width, each run is its own bucket.
    Otherwise, runs are grouped into equal-sized buckets.
    """
    n = len(timeline)
    if n == 0:
        return []
    if n <= max_width:
        return [1.0 if r.failed else 0.0 for r in timeline]

    bucket_size = n / max_width
    buckets: List[float] = []
    for i in range(max_width):
        start = int(i * bucket_size)
        end = int((i + 1) * bucket_size)
        if end <= start:
            end = start + 1
        chunk = timeline[start:end]
        fail_count = sum(1 for r in chunk if r.failed)
        buckets.append(fail_count / len(chunk))
    return buckets


def render_timeline_human(timeline: List[RunResult]) -> str:
    """Render a compact pass/fail stripe using ANSI-colored block characters.

    If timeline has more entries than MAX_TIMELINE_WIDTH, runs are bucketed.
    Each column shows: green (mostly pass), red (mostly fail), yellow (mixed).
    """
    buckets = _bucket_timeline(timeline, MAX_TIMELINE_WIDTH)
    if not buckets:
        return ""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    chars = []
    for ratio in buckets:
        if ratio >= 0.7:
            chars.append(f"{RED}▅{RESET}")
        elif ratio <= 0.3:
            chars.append(f"{GREEN}▅{RESET}")
        else:
            chars.append(f"{YELLOW}▅{RESET}")
    label = ""
    if len(timeline) > MAX_TIMELINE_WIDTH:
        label = f" ({len(timeline)} runs)"
    return "".join(chars) + label


def render_timeline_slack(timeline: List[RunResult]) -> str:
    """Render a compact pass/fail stripe for Slack using small emoji.

    If timeline has more entries than MAX_TIMELINE_WIDTH, runs are bucketed.
    Each column shows: 🟢 (mostly pass), 🔴 (mostly fail), 🟡 (mixed).
    """
    buckets = _bucket_timeline(timeline, MAX_TIMELINE_WIDTH)
    if not buckets:
        return ""
    chars = []
    for ratio in buckets:
        if ratio >= 0.7:
            chars.append("🔴")
        elif ratio <= 0.3:
            chars.append("🟢")
        else:
            chars.append("🟡")
    label = ""
    if len(timeline) > MAX_TIMELINE_WIDTH:
        label = f" _({len(timeline)} runs)_"
    return "".join(chars) + label


def truncate_left(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    return "…" + s[-(n - 1):]


def render_msg_header(state: AppState) -> str:
    return ':snowflake: Results for failing / flaky tests in ' + \
        f'<https://github.com/{state.org}/{state.repo}|{state.repo}> ({state.branch}):'


def print_for_slack(occurrences: List[Occurrence], stats: List[FileStats], state: AppState):
    most_failing = top_most_failing(stats, TOP_LIMIT)
    most_flaky = top_most_flaky(stats, TOP_LIMIT)

    content_blocks = []
    content_blocks += render_slack_list(
        f"Top {len(most_failing)} failed tests (limit={TOP_LIMIT})",
        most_failing,
        format_failing_item,
    )
    content_blocks += render_slack_list(
        f":arrows_counterclockwise: Top {len(most_flaky)} flaky tests — green → red flips (limit={TOP_LIMIT})",
        most_flaky,
        format_flaky_item,
    )

    data = {
        "channel": state.slack_channel,
        "text": "Flaky Tests Summary",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": render_msg_header(state),
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Summary window: {state.since} - {state.until}",
                }
            },
        ] + content_blocks
    }

    json = json_lib.dumps(data, indent=4)

    print(json)


def render_slack_list(title: str, items: List[FileStats], formatter) -> List[dict]:
    if not items:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{title}\n_No results_",
                },
            }
        ]

    content_blocks = []
    chunk_size = 5
    chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    for idx, chunk in enumerate(chunks):
        content = ""
        for s in chunk:
            content += formatter(s)
            content += "\n"

        header = title if idx == 0 else f"{title} (cont.)"
        content_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{header}\n{content}",
                },
                "expand": True,
            }
        )

    return content_blocks


def format_failing_item(s: FileStats) -> str:
    """Format a single failing test for Slack output.

    Example: *5x* (100%) `e2e/checkout.spec.ts`  1 2 3 4 5
    """
    nice_path = truncate_left(s.path, MAX_FILENAME_LENGTH)
    recent = sorted(s.recent_occurrences, key=lambda o: o.commit.timestamp, reverse=True)[:5]
    links = " ".join([f"<{o.check_url}|{i + 1}>" for i, o in enumerate(recent)])
    return f"*{s.fail_count}x* ({s.fail_rate:.0%}) `{nice_path}`  {links}".rstrip()


def format_flaky_item(s: FileStats) -> str:
    """Format a single flaky test for Slack output.

    Example:
    *29%* flaky · 3 flips / 10 runs · `src/auth/login.spec.ts`
    🔴🟢🔴🔴🟢🔴🟢🟢🔴🟢
    """
    nice_path = truncate_left(s.path, MAX_FILENAME_LENGTH)
    timeline = render_timeline_slack(s.run_timeline)
    return (
        f"*{s.fail_after_pass_rate:.0%}* flaky · {s.fail_after_pass} flips / {s.total_runs} runs · "
        f"`{nice_path}`\n{timeline}"
    )


def access_repo(state: AppState) -> Repository:
    auth = Auth.Token(state.auth_token)
    g = Github(auth=auth)
    o = g.get_organization(state.org)
    return o.get_repo(state.repo)


def list_occurrences(state: AppState, r: Repository) -> tuple[List[Occurrence], List[RunInfo]]:
    occurrences: List[Occurrence] = []
    runs: List[RunInfo] = []
    commits_pl = r.get_commits(sha=state.branch, since=state.since, until=state.until)
    for c in commits_pl:
        # ignore commit check suites that are not for the current branch (e.g. != master)
        ignore_commit = False
        for cs in c.get_check_suites():
            if cs.head_branch != state.branch:
                ignore_commit = True
                break
        if ignore_commit:
            continue

        c_ts = parse(c.last_modified)
        digest = CommitDigest(c.sha, c_ts)
        check_runs_pl = c.get_check_runs(filter="all")  # we want "all" runs, not just the latest one
        for cr in check_runs_pl:
            if cr.status != "completed":  # still running
                continue

            run_ts = cr.completed_at or c_ts
            failed_paths: set[str] = set()

            if cr.conclusion == "failure" and cr.output.annotations_count:
                annotations_pl = cr.get_annotations()
                for ann in annotations_pl:
                    # filter out GitHub meta annotation path, which is useless for our summary
                    if ann.path == '.github':
                        continue
                    # filter out build errors or other issues, which are not flaky tests
                    # filter out annotations that do not match the given suffixes in the file path
                    if state.path_suffixes and not ann.path.endswith(tuple(state.path_suffixes)):
                        continue
                    if not ann.message.startswith(state.prefix):
                        continue
                    # annotation path contains something like ".../packageA/TestA.xml" or ".../packageB/TestB.kt"
                    failed_paths.add(ann.path)

            runs.append(
                RunInfo(
                    name=cr.name,
                    timestamp=run_ts,
                    check_url=cr.html_url,
                    failed_paths=tuple(sorted(failed_paths)),
                )
            )

            for path in failed_paths:
                occr = Occurrence(digest, cr.html_url, path)

                # skip duplicates, if one file has multiple annotations
                if len(occurrences) > 0 and occurrences[-1] == occr:
                    continue
                occurrences.append(occr)
    return occurrences, runs


def compute_test_stats(occurrences: List[Occurrence], runs: List[RunInfo]) -> List[FileStats]:
    occurrences_by_path: Dict[str, List[Occurrence]] = {}
    for o in occurrences:
        occurrences_by_path.setdefault(o.annotation_path, []).append(o)

    total_runs_by_check: Dict[str, int] = {}
    runs_by_check: Dict[str, List[RunInfo]] = {}
    fail_counts: Dict[str, int] = {}
    test_to_checks: Dict[str, set[str]] = {}

    for run in runs:
        total_runs_by_check[run.name] = total_runs_by_check.get(run.name, 0) + 1
        runs_by_check.setdefault(run.name, []).append(run)
        for path in run.failed_paths:
            fail_counts[path] = fail_counts.get(path, 0) + 1
            test_to_checks.setdefault(path, set()).add(run.name)

    fail_after_pass: Dict[str, int] = {}
    flip_events: Dict[str, List[FlipEvent]] = {}
    known_tests_per_check: Dict[str, set[str]] = {}
    for check_name, check_runs in runs_by_check.items():
        check_runs.sort(key=lambda r: r.timestamp)
        known_tests: set[str] = set()
        last_status: Dict[str, bool] = {}
        last_pass_run: Dict[str, RunInfo] = {}
        for run in check_runs:
            failed = set(run.failed_paths)
            for test in known_tests - failed:
                last_status[test] = False
                last_pass_run[test] = run
            for test in failed:
                if test in last_status and last_status[test] is False:
                    fail_after_pass[test] = fail_after_pass.get(test, 0) + 1
                    prev = last_pass_run[test]
                    flip_events.setdefault(test, []).append(
                        FlipEvent(
                            test_path=test,
                            check_name=check_name,
                            passed_at=prev.timestamp,
                            passed_url=prev.check_url,
                            failed_at=run.timestamp,
                            failed_url=run.check_url,
                        )
                    )
                last_status[test] = True
                known_tests.add(test)
        known_tests_per_check[check_name] = known_tests

    # Build per-test timeline: for each test, collect all runs from relevant checks
    # sorted by time, showing whether the test failed in that run or not.
    test_timelines: Dict[str, List[RunResult]] = {}
    for check_name, check_runs in runs_by_check.items():
        # check_runs already sorted by timestamp from the loop above
        for run in check_runs:
            failed_set = set(run.failed_paths)
            # Only include runs for checks that are relevant to at least one known test
            for test in known_tests_per_check.get(check_name, set()):
                test_timelines.setdefault(test, []).append(
                    RunResult(
                        timestamp=run.timestamp,
                        check_url=run.check_url,
                        check_name=check_name,
                        failed=test in failed_set,
                    )
                )
    # Sort each timeline by timestamp
    for tl in test_timelines.values():
        tl.sort(key=lambda r: r.timestamp)

    stats: List[FileStats] = []
    for path, fail_count in fail_counts.items():
        checks = test_to_checks.get(path, set())
        total_runs = sum(total_runs_by_check.get(name, 0) for name in checks)
        if total_runs == 0:
            continue
        fap = fail_after_pass.get(path, 0)
        stats.append(
            FileStats(
                path=path,
                fail_count=fail_count,
                total_runs=total_runs,
                fail_rate=fail_count / total_runs,
                fail_after_pass=fap,
                fail_after_pass_rate=fap / total_runs,
                recent_occurrences=occurrences_by_path.get(path, []),
                flip_events=sorted(flip_events.get(path, []), key=lambda e: e.failed_at),
                run_timeline=test_timelines.get(path, []),
            )
        )

    return stats


def top_most_failing(stats: List[FileStats], limit: int) -> List[FileStats]:
    return sorted(
        stats,
        key=lambda s: (s.fail_count, s.fail_rate),
        reverse=True,
    )[:limit]


def top_most_flaky(stats: List[FileStats], limit: int) -> List[FileStats]:
    return sorted(
        stats,
        key=lambda s: (s.fail_after_pass_rate, s.fail_after_pass, s.fail_rate),
        reverse=True,
    )[:limit]


def main():
    state: AppState = parse_args()
    r = access_repo(state)
    occurrences, runs = list_occurrences(state, r)
    stats = compute_test_stats(occurrences, runs)
    if state.slack_channel:
        print_for_slack(occurrences, stats, state)
    else:
        print_for_humans(occurrences, stats)


if __name__ == '__main__':
    main()
