# Releasing

This repo uses [release-please](https://github.com/googleapis/release-please) to
automate version bumps, changelog entries, and GitHub Releases. You do not bump
versions or write changelog entries by hand.

## How a release happens

Releases are cut automatically when releasable work lands on `main`:

1. Merge a PR to `main` whose squash commit uses a
   [conventional commit](https://www.conventionalcommits.org/) prefix that
   release-please treats as releasable:
   - `feat:` — minor bump (e.g. `1.2.1` → `1.3.0`)
   - `fix:` — patch bump (e.g. `1.2.1` → `1.2.2`)
   - `feat!:` / `fix!:` (or a `BREAKING CHANGE` note) — major bump
2. The push to `main` triggers the `Release Please` workflow
   (`.github/workflows/release-please.yml`).
3. release-please opens a release PR that bumps the version in
   `bible/info.json` and updates `CHANGELOG.md`.
4. The workflow auto-merges that release PR (squash) as soon as CI passes.
5. Merging the release PR is itself a push to `main`, so release-please then
   cuts the tag (e.g. `v1.3.0`) and creates the GitHub Release.

Non-releasable prefixes (`chore:`, `docs:`, `refactor:`, `build:`, `test:`,
`ci:`) do not trigger a release — the workflow runs and no-ops.

## Forcing a specific version

To release an exact version regardless of the conventional-commit bump, add a
`Release-As: x.x.x` footer (case-insensitive) to the commit message that lands
on `main`.

Because this repo squash-merges, put it in the **squash commit message** when
merging the PR:

```text
chore: release 1.5.0

Release-As: 1.5.0
```

release-please then opens a release PR for exactly `1.5.0`, and the
auto-merge step merges it once CI is green.

> The directive is read from the commit message on `main`, not the PR body.
> You may keep a reminder in the PR body, but it must also be in the squash
> commit message for release-please to pick it up.

## Manual trigger

You can run the workflow on demand (Actions → "Release Please" → Run workflow).
It uses the same logic as the automatic trigger, so it only produces a release
if there are releasable commits — or a `Release-As` footer — since the last
release. Use it to re-evaluate after a failed run or to cut a release early.

## Branch protection

`main` is protected by the `release-main-on-ci-success` ruleset so the
auto-merge is safe:

- Requires the `test` status check to pass (strict / up-to-date).
- No pull request review requirement, so auto-merge is not blocked.
- No commit signature requirement (release-please commits are unsigned).
- Linear history required (compatible with squash merges).
- Branch deletion and force-push are blocked.

## Version source of truth

The version lives in `bible/info.json` (`version`). `bible/bible.py` derives
`Bible.VERSION` from it at import. release-please updates `bible/info.json`
via its `extra-files` config — do not hardcode the version back into
`bible/bible.py`.
