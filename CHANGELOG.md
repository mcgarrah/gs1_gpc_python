# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2025-06-15

### Added
- New class-based API with GPCDownloader, GPCParser, and GPCExporter classes
- Added target_directory parameter to download_latest_gpc_xml()
- New example for filtering and importing only the Food/Beverage segment
- Enhanced documentation for the new class-based API
- Improved code comments for better readability and onboarding

### Changed
- Refactored function-based API to use class-based approach
- Updated CLI to use new class-based API with additional options
- Reorganized internal processing logic for better maintainability
- Enhanced error handling and fallback mechanisms

### Fixed
- Improved handling of download directory paths
- Better error messages when files are not found

## [0.1.5] - 2025-06-01

### Added
- Updated release process documentation to align with other projects
- Improved GitHub Actions workflow documentation

### Fixed
- Fixed documentation for Github repo name `gs1_gpc_import` rename to `gs1_gpc_python`

### Removed
- Removed empty CLI module from API reference documentation

## [0.1.4] - 2025-05-30

### Added
- Added requirements-postgresql.txt for PostgreSQL dependencies
- Improved documentation for database configuration
- Enhanced CLI error handling

### Changed
- Updated dependency versions
- Optimized XML parsing for large files
- Improved cross-platform compatibility

### Fixed
- Fixed connection handling for PostgreSQL databases
- Resolved path issues on Windows systems

## [0.1.3] - 2025-05-28

### Added
- Support for additional data formats
- Enhanced error reporting

### Changed
- Improved performance for large dataset processing
- Updated documentation with more examples

### Fixed
- Issue with database connection handling
- Path resolution for cross-platform compatibility

## [0.1.2] - 2025-05-27

### Added
- PyPI publication metadata
- GitHub Release workflow integration

### Changed
- Enhanced release automation process

### Fixed
- Package distribution configuration

## [0.1.1] - 2023-05-27

### Added
- Initial release as a pip installable module
- Modular package structure with separate components
- Command-line interface using Click
- Support for both SQLite and PostgreSQL databases
- Documentation with Sphinx and ReadTheDocs configuration
- PDF documentation generation
- Automated version update script
- GitHub Actions workflow for releases

### Changed
- Refactored from single script to modular package
- Improved error handling and logging
- Enhanced database abstraction layer
- Standardized command naming to `import-gpc`

### Fixed
- Path handling for data directories
- Package installation issues with multiple top-level packages
- Documentation command references