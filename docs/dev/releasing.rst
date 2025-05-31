Releasing
=========

This document describes the process for releasing new versions of the GS1 GPC Python Client.

Prerequisites
------------

1. Install the GitHub CLI (``gh``):

   .. code-block:: bash

      # For macOS
      brew install gh
      
      # For Linux
      sudo apt install gh  # Debian/Ubuntu
      sudo dnf install gh  # Fedora
      
      # For Windows
      winget install --id GitHub.cli

2. Authenticate with GitHub:

   .. code-block:: bash

      gh auth login

3. Install build and twine:

   .. code-block:: bash

      pip install build twine

Version Numbering
---------------

This project follows `Semantic Versioning <https://semver.org/>`_:

- **MAJOR** version for incompatible API changes
- **MINOR** version for adding functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

Release Process
-------------

1. Ensure all tests pass and the code is ready for release:

   .. code-block:: bash

      # Run tests
      pytest gs1_gpc/tests/
      
      # Check code quality
      flake8 gs1_gpc
      black --check gs1_gpc

2. Update Version Numbers
^^^^^^^^^^^^^^^^^^^^^^^

   Use the version update script to update the version number in all necessary files:

   .. code-block:: bash

      python version_update.py X.Y.Z

   This will update the version in:
   
   - ``gs1_gpc/__init__.py``
   - ``pyproject.toml``
   - ``setup.cfg`` (if it exists)
   - ``setup.py`` (if it exists)

3. Update Changelog
^^^^^^^^^^^^^^^^

   Update the ``CHANGELOG.md`` file with the changes in the new version:

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

4. Create a Pull Request (if working on a feature branch)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   .. code-block:: bash

      # Ensure you're on your feature branch with latest changes
      git checkout feature-branch
      git pull origin feature-branch

      # Commit version changes
      git add .
      git commit -m "Bump version to vX.Y.Z"
      git push origin feature-branch

      # Create a pull request
      gh pr create --base main --head feature-branch --title "Release vX.Y.Z" --body "Release version X.Y.Z with the following changes:
      - Feature 1
      - Feature 2
      - Bug fix 1"

5. Review and Merge the Pull Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   .. code-block:: bash

      # List open pull requests
      gh pr list

      # View the pull request
      gh pr view [PR_NUMBER]

      # Merge the pull request
      gh pr merge [PR_NUMBER] --merge

6. Create and Push a Tag
^^^^^^^^^^^^^^^^^^^^

   .. code-block:: bash

      # Switch to main branch
      git checkout main
      git pull origin main

      # Create an annotated tag
      git tag -a vX.Y.Z -m "Version X.Y.Z"
      
      # Push the tag
      git push origin vX.Y.Z

7. Automated GitHub Release and PyPI Publishing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   Once you push a tag in the format `vX.Y.Z`, the GitHub Actions workflow defined in `.github/workflows/publish-to-pypi.yml` will automatically:

   1. Build the package
   2. Create a GitHub release with the built package files
   3. Upload the package to PyPI

   You can monitor the workflow progress in the "Actions" tab of your GitHub repository.

Release Checklist
--------------

Before releasing, ensure:

- All tests pass
- Documentation is up to date
- CHANGELOG.md is updated
- Version numbers are consistent
- All changes are committed and pushed

Post-Release
-----------

After releasing, update the version number to the next development version:

.. code-block:: bash

   python version_update.py X.Y.(Z+1)-dev

Commit this change:

.. code-block:: bash

   git checkout main  # or your development branch
   git add .
   git commit -m "Bump version to X.Y.(Z+1)-dev"
   git push origin main  # or your development branch