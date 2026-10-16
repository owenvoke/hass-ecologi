# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com), and this project adheres to [Semantic Versioning](https://semver.org).

## Unreleased

### Changed
- Require Home Assistant 2026.9 or later
- Trees and carbon offset are numeric measurements, so they appear in long-term statistics
- Sensor names are now translated and use sentence case

### Fixed
- Network errors in the config flow showed an unknown error, and an unknown username had no error message
- Update failures are now reported to Home Assistant, which retries them
- The options flow used a deprecated API that no longer works on current Home Assistant

## v0.1.6 - 2023-11-01

### Fixed
- Ensure that updates to configuration are actually applied

## v0.1.5 - 2023-10-20

### Fixed
- Ensure only the current config entry is removed

## v0.1.4 - 2023-07-05

### Fixed
- Resolve invalid return type

## v0.1.3 - 2023-07-05

### Fixed
- Resolve checkout on release

## v0.1.2 - 2023-07-05

### Added
- Add support to update interval

## v0.1.1 - 2022-11-09

### Changed
- Change default scan interval to every 2 hours
- Apply style fixes from Black

## v0.1.0 - 2022-11-09

### Added
- Initial release
