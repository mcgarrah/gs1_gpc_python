Releasing
=========

This document provides information about releasing new versions of the GS1 GPC project.

Version Numbering
---------------

We use semantic versioning (SemVer) for version numbers:

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

Release Process
------------

1. Ensure all tests pass and the code is ready for release:

   .. code-block:: bash

      # Run tests
      pytest gs1_gpc/tests/
      
      # Check code quality
      flake8 gs1_gpc
      black --check gs1_gpc

2. Update the version using the version_update.py script:

   .. code-block:: bash

      # Update version to X.Y.Z
      python version_update.py X.Y.Z

   This will update the version in:
   
   - ``gs1_gpc/__init__.py``
   - ``pyproject.toml``
   - ``setup.cfg`` (if it exists)
   - ``setup.py`` (if it exists)

3. Update CHANGELOG.md with the changes in the new version:

   .. code-block:: markdown

      ## [X.Y.Z] - YYYY-MM-DD
      
      ### Added
      - New feature 1
      - New feature 2
      
      ### Changed
      - Change 1
      - Change 2
      
      ### Fixed
      - Bug fix 1
      - Bug fix 2

4. Commit the changes:

   .. code-block:: bash

      git add gs1_gpc/__init__.py pyproject.toml setup.py setup.cfg CHANGELOG.md
      git commit -m "Bump version to X.Y.Z"

5. Create and push a tag using GitHub CLI:

   .. code-block:: bash

      # Create an annotated tag
      git tag -a vX.Y.Z -m "Version X.Y.Z"
      
      # Push the changes and tag
      git push origin main
      git push origin vX.Y.Z

6. Create a GitHub release using GitHub CLI:

   .. code-block:: bash

      # Create a release from the tag
      gh release create vX.Y.Z --title "GS1 GPC X.Y.Z" --notes-file RELEASE_NOTES.md
      
   Or for a simpler release:
   
   .. code-block:: bash

      # Create a release with notes from the tag message
      gh release create vX.Y.Z --generate-notes

7. Build and publish the package to PyPI:

   .. code-block:: bash

      # Install build tools if not already installed
      pip install build twine
      
      # Build the package
      python -m build
      
      # Upload to PyPI
      python -m twine upload dist/*

Release Checklist
--------------

Before releasing, ensure:

- All tests pass
- Documentation is up to date
- CHANGELOG.md is updated
- Version numbers are consistent
- All changes are committed and pushed

Automating Releases with GitHub Actions
------------------------------------

You can also set up GitHub Actions to automate the release process. Create a workflow file at ``.github/workflows/release.yml`` with the following content:

.. code-block:: yaml

   name: Release

   on:
     push:
       tags:
         - 'v*.*.*'

   jobs:
     release:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.12'
             
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install build twine
             
         - name: Build package
           run: python -m build
           
         - name: Create GitHub Release
           uses: softprops/action-gh-release@v1
           with:
             generate_release_notes: true
             files: dist/*
             
         - name: Publish to PyPI
           env:
             TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
             TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
           run: twine upload dist/*

With this workflow, when you push a tag in the format `vX.Y.Z`, GitHub Actions will automatically:

1. Build the package
2. Create a GitHub release
3. Upload the package to PyPI