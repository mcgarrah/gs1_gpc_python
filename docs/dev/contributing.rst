Contributing
===========

We welcome contributions to the GS1 GPC Import project! This document provides guidelines for contributing to the project.

Setting Up Development Environment
-------------------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/mcgarrah/gs1_gpc_import.git
      cd gs1_gpc_import

2. Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install development dependencies:

   .. code-block:: bash

      pip install -r requirements.txt
      pip install -e ".[dev]"

Code Style
---------

We use the following tools to maintain code quality:

- **Black**: Code formatter
- **Flake8**: Linter
- **isort**: Import sorter
- **mypy**: Type checker

You can run these tools with:

.. code-block:: bash

   # Format code
   black gs1_gpc

   # Sort imports
   isort gs1_gpc

   # Lint code
   flake8 gs1_gpc

   # Type check
   mypy gs1_gpc

Pull Request Process
-----------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

When submitting a pull request, please:

- Include a clear description of the changes
- Update documentation if necessary
- Add tests for new features
- Ensure all tests pass

Testing
------

We use pytest for testing. Run the tests with:

.. code-block:: bash

   pytest

To run tests with coverage:

.. code-block:: bash

   pytest --cov=gs1_gpc

Documentation
-----------

We use Sphinx for documentation. To build the documentation:

.. code-block:: bash

   cd docs
   make html

The documentation will be built in the ``docs/_build/html`` directory.