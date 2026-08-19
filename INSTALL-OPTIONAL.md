# Installing the Bible Cog: Branch and Main Options

This document covers installing the Bible cog from a specific branch, and switching
between the `main` branch and a feature branch.

## Install from a branch

`.repo add` takes an optional `[branch]` argument.

Explicit branch:

```text
.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog <branch>
```

Or a tree URL, where the branch is extracted automatically:

```text
.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog/tree/<branch>
```

If no branch is given, the default branch (`main`) is cloned.

The chosen branch is stored in Redbot's config. `.repo update` tracks that branch.

## Have both main and a branch

Redbot has no `repo checkout` command, so a single repo entry cannot switch branches.
To keep both, add the same URL twice under different names. Each name is its own clone
on its own branch.

```text
.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog
.repo add anvil-dev https://github.com/fight-the-good-fight/redbot-bible-cog <branch>
```

## Switch between them

Reinstall the cog from the other repo. `copy_to` overwrites all files in the target
directory, so the second install replaces the first.

To use the branch build:

```text
.cog install anvil-dev bible
.load bible
```

To go back to main:

```text
.cog install anvil bible
.load bible
```

## Notes

- Each repo entry is a separate clone. `.repo update anvil` and `.repo update anvil-dev`
  each track their own branch.
- The installed cog remembers the last repo it was installed from. `.cog update bible`
  updates from that repo.
- `.cog installversion <repo> <revision>` pins a specific commit. That is a different
  mechanism from branch switching.