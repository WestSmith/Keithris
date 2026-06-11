# Keithris — instructions for Claude

A PWA Tetris game by Shawn (GitHub: **WestSmith**), built with his boyfriend Keith.

- Repo: `WestSmith/Keithris` (public) · Live: https://westsmith.github.io/Keithris/
- This folder is deploy staging — it mirrors what's on GitHub's `main` branch.
- **Never touch `WestSmith/SpellCoco`** — separate project, same account.

## Deploying

```
GITHUB_TOKEN=<token> python3 deploy.py status
GITHUB_TOKEN=<token> python3 deploy.py push -m "vNN: message" index.html
```

The token lives ONLY in Claude's project memory and the `GITHUB_TOKEN` env var.
**Never write it into any file in this folder** — everything here gets pushed to a
public repo. Before any push, verify the files don't contain it (deploy.py also
aborts if it spots one).

GitHub Pages serves from `main` branch root; redeploys ~30–60s after a push.
Verify after deploying (fetch the live site and check the version marker).

## Workflow conventions

- Deploying is part of the release workflow: once a version is built, push without
  asking, then verify the live site picked it up.
- Version history: save each release as `keithrisvNN.<ext>` in an archive folder AND
  copy it into this folder under its deploy name (e.g. `index.html`) before pushing.
- Put a `<!-- vNN -->` marker in index.html so deploys are verifiable.

## PWA notes

- Pages serves at the `/Keithris/` subpath: manifest `start_url`/`scope` and service
  worker registration paths must be relative or subpath-aware.

## Accessibility (hard requirements)

Keith has a visual impairment and uses OS + browser zoom:

- Target WCAG AAA contrast.
- Avoid fixed widths that clip content under zoom.
- Test narrow viewports and high zoom levels.
