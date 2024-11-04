===============================
InvestorCalculator Project
===============================

InvestorCalculator is a Python-based application designed to help manage and analyze company financial data. It provides functionalities to insert data, display key financial metrics, manage company records, and display insights such as the top ten companies based on various financial criteria.

Project Features
----------------

The InvestorCalculator includes the following core features:

1. **Company Data Management:**

   - Add new companies with their basic information (ticker, name, sector).
   - Read and display detailed company information, including financial metrics.
   - Update existing company and financial records.
   - Delete company records from the database.
   - List all stored companies in alphabetical order by their ticker.

2. **Financial Data Handling:**

   - Load and insert financial data from CSV files stored in a `data` directory.
   - Automatically create and populate the database with company and financial data.
   - Clear the database of all existing records.

3. **Top Ten Analysis:**

   - Display the top ten companies based on selected financial metrics:
     - ND/EBITDA (Net Debt to EBITDA)
     - ROE (Return on Equity)
     - ROA (Return on Assets)
   - Sort results and display them in descending order.

4. **Calculation of Key Financial Ratios:**

   - Compute and display important financial ratios such as:
     - P/E (Price to Earnings)
     - P/S (Price to Sales)
     - P/B (Price to Book)
     - ND/EBITDA
     - ROE
     - ROA
     - L/A (Liabilities to Assets)

Installation Guide
------------------

**Prerequisites**

To run InvestorCalculator, you need the following installed:

- **Python 3.8+**
- **SQLAlchemy** (for database management)
- **unittest** (for testing)

**Setup Steps**

1. **Cloning the Repository:**

   Clone the project repository using the following command:

   .. code-block:: bash

      git clone https://github.com/RafaelKarcz/InvestorCalculator.git

2. **Creating a Python Virtual Environment:**

   It is recommended to create an isolated environment:

   .. code-block:: bash

      python -m venv investor_env

   Activate the environment:

   - On Windows:
     
     .. code-block:: bash

        investor_env\Scripts\activate

   - On macOS/Linux:
     
     .. code-block:: bash

        source investor_env/bin/activate

3. **Installing Dependencies:**

   Install SQLAlchemy using `pip`:

   .. code-block:: bash

      pip install sqlalchemy

4. **Running the Application:**

   Run the main program:

   .. code-block:: bash

      python investor_calculator.py

   This will launch the application and present the main menu for database and financial data management.

User Commands
-------------

After starting the program, the following commands are available:

- **CRUD operations**:
  - Create, read, update, and delete companies and their financial data.
  - List all companies stored in the database.

- **Top Ten Analysis**:
  - Display the top ten companies based on financial criteria (ND/EBITDA, ROE, ROA).

Example Usage
-------------

Here is an example session demonstrating how to use InvestorCalculator:

.. code-block:: text

   Welcome to the Investor Program!
   MAIN MENU
   0 Exit
   1 CRUD operations
   2 Show top ten companies by criteria

   Enter an option:
   1
   CRUD MENU
   0 Back
   1 Create a company
   2 Read a company
   3 Update a company
   4 Delete a company
   5 List all companies

   Enter an option:
   5
   COMPANY LIST
   AAPL Apple Inc. Technology
   GOOG Google LLC Technology

Running Unit Tests
------------------

This project includes unit tests for validating the database and data management functionalities. To run the tests, navigate to the project directory and use:

.. code-block:: bash

   python -m unittest test_investor_calculator.py

Directory Structure
-------------------

The project directory contains the following files:

.. code-block:: text

   ├── data/
   │   ├── companies.csv                # Sample company data for testing
   │   └── financial.csv                # Sample financial data for testing
   ├── investor_calculator.py           # Main application file
   ├── test_investor_calculator.py      # Unit tests for the application
   ├── README.rst                       # Project documentation
   ├── LICENSE                          # Project license
   └── .gitignore                       # Git ignore rules

Contributing
------------

Contributions to this project are welcome. If you find a bug or have a feature request, please submit an issue or a pull request on the project repository.

License
-------

This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details.
