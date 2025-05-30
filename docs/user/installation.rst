Installation
============

Requirements
-----------

* Python 3.8 or higher
* GPCC 1.1.0 or higher library

Installing from PyPI
-------------------

Install the package:

.. code-block:: bash

   pip install gs1-gpc

Installing from Source
--------------------

.. code-block:: bash

   git clone https://github.com/mcgarrah/gs1_gpc_import.git
   cd gs1_gpc_import
   
   # Create and activate a virtual environment (recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies including gpcc from GitHub
   pip install -r requirements.txt
   
   # Install the package in development mode
   pip install -e .

PostgreSQL Support
----------------

To use PostgreSQL instead of SQLite, install the PostgreSQL extra:

.. code-block:: bash

   pip install gs1-gpc[postgresql]

Or when installing from source:

.. code-block:: bash

   pip install -e ".[postgresql]"

Development Installation
---------------------

For development, you can install additional dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

This will install testing and code quality tools like pytest, black, flake8, etc.