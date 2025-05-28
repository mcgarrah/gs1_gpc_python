# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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