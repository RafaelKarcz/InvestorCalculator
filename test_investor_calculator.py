import unittest
from unittest.mock import patch, mock_open
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from investor_calculator import DatabaseConnection, Company, Financial, Base
import os


class TestDatabaseConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up a temporary SQLite database for testing.
        """
        # Create an in-memory SQLite database for testing purposes
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(cls.engine)  # Create tables in the in-memory database

    def setUp(self):
        """
        Create a new session before each test.
        """
        self.session = self.Session()

    def tearDown(self):
        """
        Rollback any changes and close the session after each test.
        """
        self.session.rollback()
        self.session.close()

    def test_insert_company(self):
        """
        Test inserting a company into the database.
        """
        # Create a DatabaseConnection instance (using the in-memory DB for testing)
        db_connection = DatabaseConnection('sqlite:///:memory:')
        
        # Insert a company
        new_company = Company(ticker="AAPL", name="Apple Inc.", sector="Technology")
        self.session.merge(new_company)
        self.session.commit()

        # Query the company to ensure it was inserted
        result = self.session.query(Company).filter_by(ticker="AAPL").first()

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "AAPL")
        self.assertEqual(result.name, "Apple Inc.")
        self.assertEqual(result.sector, "Technology")

    def test_insert_financial(self):
        """
        Test inserting a financial record into the database.
        """
        # Create a DatabaseConnection instance (using the in-memory DB for testing)
        db_connection = DatabaseConnection('sqlite:///:memory:')
        
        # Insert a company and its financial record
        new_company = Company(ticker="AAPL", name="Apple Inc.", sector="Technology")
        new_financial = Financial(
            ticker="AAPL",
            ebitda=1000000.0,
            sales=2000000.0,
            net_profit=500000.0,
            market_price=150.0,
            net_debt=100000.0,
            assets=3000000.0,
            equity=1500000.0,
            cash_equivalents=500000.0,
            liabilities=2000000.0
        )
        self.session.merge(new_company)
        self.session.merge(new_financial)
        self.session.commit()

        # Query the financial record to ensure it was inserted
        result = self.session.query(Financial).filter_by(ticker="AAPL").first()

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "AAPL")
        self.assertEqual(result.ebitda, 1000000.0)

    def test_clear_database(self):
        """
        Test clearing the database by deleting all rows.
        """
        db_connection = DatabaseConnection('sqlite:///:memory:')
        
        # Insert a company and financial data using the session from db_connection
        with db_connection.Session() as session:
            new_company = Company(ticker="GOOG", name="Google LLC", sector="Technology")
            new_financial = Financial(ticker="GOOG", ebitda=123.45, sales=678.9, net_profit=50.5)
            session.merge(new_company)
            session.merge(new_financial)
            session.commit()

        # Clear the database
        db_connection.clear_database()

        # Re-query to ensure the tables are empty
        with db_connection.Session() as session:
            company_count = session.query(Company).count()
            financial_count = session.query(Financial).count()

        # Assertions
        self.assertEqual(company_count, 0)
        self.assertEqual(financial_count, 0)

    @patch('builtins.open', new_callable=mock_open, read_data='ticker,name,sector\nAAPL,Apple Inc.,Technology')
    @patch('csv.DictReader')
    def test_insert_data(self, mock_dict_reader, mock_file):
        """
        Test inserting data from CSV into the database.
        """
        # Prepare mock CSV data
        mock_dict_reader.return_value = [{'ticker': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'}]

        # Create the database connection
        db_connection = DatabaseConnection('sqlite:///:memory:')
        
        # Call insert_data (force_reload=True to ensure it inserts)
        db_connection.insert_data(force_reload=True)

        # Query the inserted data
        result = self.session.query(Company).filter_by(ticker='AAPL').first()

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "AAPL")
        self.assertEqual(result.name, "Apple Inc.")
        self.assertEqual(result.sector, "Technology")

    @patch('builtins.open', new_callable=mock_open, read_data='ticker,ebitda,sales\nAAPL,1000000.0,2000000.0')
    @patch('csv.DictReader')
    def test_insert_financial_data(self, mock_dict_reader, mock_file):
        """
        Test inserting financial data from CSV into the database.
        """
        # Prepare mock CSV data for financial records
        mock_dict_reader.return_value = [{'ticker': 'AAPL', 'ebitda': '1000000.0', 'sales': '2000000.0'}]

        # Create the database connection
        db_connection = DatabaseConnection('sqlite:///:memory:')
        
        # Insert a dummy company for foreign key constraint
        new_company = Company(ticker="AAPL", name="Apple Inc.", sector="Technology")
        with db_connection.Session() as session:
            session.merge(new_company)
            session.commit()

        # Call insert_data (force_reload=True to ensure it inserts)
        db_connection.insert_data(force_reload=True)

        # Query the inserted financial data
        result = self.session.query(Financial).filter_by(ticker='AAPL').first()

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "AAPL")
        self.assertEqual(result.ebitda, 1000000.0)
        self.assertEqual(result.sales, 2000000.0)


if __name__ == '__main__':
    unittest.main()