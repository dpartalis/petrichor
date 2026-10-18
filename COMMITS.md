# Commit Convention

This repo follows a trimmed-down [Conventional Commits](https://www.conventionalcommits.org/)
style. The goal: a git history you can scan in one glance, and changelogs that write
themselves.

## Format

```
<type>(<scope>): <short imperative summary>

[optional body: what & why, not how]

[optional footer: BREAKING CHANGE: ... / closes #123]
```

**Example:**

```
feat(cli): add --delta flag for Delta Lake logging
```

## Rules

1. **Type** — required, lowercase, from this fixed list:

   | Type | When | Version bump |
   |---|---|---|
   | `feat` | new user-facing capability | minor (0.x.0) |
   | `fix` | bug fix | patch (0.0.x) |
   | `docs` | README, comments, docs | none |
   | `test` | adding/changing tests only | none |
   | `refactor` | code change, no behavior change | none |
   | `chore` | deps, CI, .gitignore, tooling, logs | none |

   Six types, deliberately. CI changes fold into `chore` until the repo needs more.

2. **Scope** — optional, one of the module names:
   `cli`, `balance`, `weather`, `config`, `storage`, `report`, `action`, `deps`.

3. **Summary** — imperative mood ("add", not "added"), ≤ 72 characters,
   lowercase after the colon, no trailing period.

4. **Body** — only when the *why* isn't obvious. One or two sentences, max.

5. **Breaking changes** — put `BREAKING CHANGE: <description>` in the footer.

## What good looks like

```
feat(cli): add report subcommand with season summary
feat(balance): support FAO-56 crop coefficients per zone
fix(weather): handle null precipitation values from Open-Meteo
chore(action): add daily scheduled watering workflow
docs: document delta logging in README
test(storage): cover CSV append without duplicate header
```

## Handy queries

```bash
git log --oneline --grep="^feat"          # every feature ever added
git log v0.1.0..HEAD --grep="^feat\|^fix" # instant changelog for a release
```

## Versioning tie-in

Pre-1.0 SemVer: `feat` bumps minor, `fix` bumps patch, `BREAKING CHANGE` bumps minor
while pre-1.0. The commit type tells you the next version number.

## Commit template

A `.gitmessage` cheatsheet lives in the repo root. Enable it once per clone:

```bash
git config commit.template .gitmessage
```

Then plain `git commit` (without `-m`) opens your editor with the type/scope
reference right in the buffer.

## Automated commits

Commits made by the GitHub Actions daily workflow use:

```
chore(log): daily water balance
```

so they sort into the convention and are easy to filter out of the history.
