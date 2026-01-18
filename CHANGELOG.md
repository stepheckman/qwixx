# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] [2026-01-18]

### Added
- Created `/changelog` workflow in `.agent/workflows/changelog.md` to automate session summaries and git operations.

## [1.1.0] [2026-01-18]

### Added
- Added `default`, `test-frontend`, and unified `test` recipes to `justfile`.
- Configured Vitest in `frontend/vite.config.js` for frontend testing.
- Added `tests` volume mount to `docker-compose.yml` for backend test access.

### Changed
- Refactored backend tests in `tests/` directory to use `app.core` imports, aligning with the new project structure.
- Updated `justfile` to include detailed test recipes and a default command list.
