# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3] - 2026-02-16

### Added
- Added `remove_fields_from_fieldsets` utility function for removing one or multiple field names from Django admin fieldsets

## [0.2] - 2025-04-14

### Changed
- Modified the `auto_add_fields_to_fieldsets` function to no longer exclude readonly fields

## [0.1] - 2025-04-14

### Added
- Initial release of django-auto-admin-fieldsets
- Added `AutoFieldsetsMixin` for automatically handling unspecified fields in admin fieldsets
- Added `AutoFieldsetsModelAdmin` as a convenience class
- Added `auto_add_fields_to_fieldsets` utility function
