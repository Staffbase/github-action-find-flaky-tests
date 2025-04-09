# 🔎 FindFlakyTests Action

A GitHub Action that finds flaky tests in a repository based on the test runs of a given branch.
Afterward, it posts a comment in a given Slack channel with the results.

```yaml
name: Find flaky tests
on:
  # At 05:00 on Monday.
  schedule:
    - cron: '0 5 * * 1'

jobs:
  flaky_tests:
    name: Flaky tests
    runs-on: ubuntu-latest
    steps:
      - name: Find flaky tests
        uses: Staffbase/github-action-find-flaky-tests@<version>
        with:
          # identifier for the slack channel
          slack-channel-id: 45678787976
          # name of the slack channel
          slack-channel-name: '#flaky-tests'
          # optional: name of the repository where it should check, default: current repository
          repository: 'Staffbase/test-flaky'
          # optional: name of the branch where it should check, default: main
          branch: 'master'
          # optional: prefix of the test run, default: 'test'
          prefix: 'test-'
          # URL of the Slack incoming webhooks
          slack-incoming-webhooks-url: ${{ secrets.SLACK_INCOMING_WEBHOOKS_URL }}
          # GitHub token
          token: ${{ secrets.GITHUB_TOKEN }}
```

## Release 🔖

To create a new release just use [this page][release-new] and publish the draft release.

## Contributing 👥

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

<table>
  <tr>
    <td>
      <img src="docs/assets/images/staffbase.png" alt="Staffbase GmbH" width="96" />
    </td>
    <td>
      <b>Staffbase GmbH</b>
      <br />Staffbase is an internal communications platform built to revolutionize the way you work and unite your company. Staffbase is hiring: <a href="https://jobs.staffbase.com" target="_blank" rel="noreferrer">jobs.staffbase.com</a>
      <br /><a href="https://github.com/Staffbase" target="_blank" rel="noreferrer">GitHub</a> | <a href="https://staffbase.com/" target="_blank" rel="noreferrer">Website</a> | <a href="https://jobs.staffbase.com" target="_blank" rel="noreferrer">Jobs</a>
    </td>
  </tr>
</table>

[release-new]: https://github.com/Staffbase/github-action-find-flaky-tests/releases
