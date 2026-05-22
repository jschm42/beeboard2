# Release Compliance Checklist

This checklist is used to prepare and publish BeeBoard releases.

## 1. Scope and Version

- [ ] Confirm target version in VERSION file.
- [ ] Confirm release type (stable or pre-release).
- [ ] Ensure release notes draft exists for this version.

## 2. Quality Gates

- [ ] Backend lint passes: `ruff check backend/app backend/tests`.
- [ ] Backend tests pass: `pytest backend/tests`.
- [ ] Frontend lint passes: `npm run lint` in `frontend`.
- [ ] Frontend build passes: `npm run build` in `frontend`.

## 3. Security and Compliance

- [ ] Ensure no secrets are committed.
- [ ] Validate `.env.example` remains safe for publishing.
- [ ] Review THIRD_PARTY_NOTICES.md for dependency/license updates.

## 4. Release Artifacts

- [ ] Finalize release notes markdown for the target version.
- [ ] Include known limitations and migration hints (if any).
- [ ] Include verification notes (what was tested).

## 5. Git and Tagging

- [ ] Confirm branch is up to date with `main`.
- [ ] Commit release preparation files.
- [ ] Create annotated tag: `git tag -a v<version> -m "Release <version>"`.
- [ ] Push commits and tags: `git push origin main --tags`.

## 6. GitHub Release

- [ ] Create GitHub release from tag `v<version>`.
- [ ] Mark as pre-release when version contains alpha/beta/rc.
- [ ] Paste prepared release notes.
- [ ] Publish release.

## 7. Post-Release

- [ ] Verify release appears on GitHub Releases page.
- [ ] Verify downloadable source archives are available.
- [ ] Announce release to users.
