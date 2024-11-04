from abc import ABC, abstractmethod
from typing import Dict
from sqlalchemy import create_engine, Column, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import csv
import os
import traceback

# SQLAlchemy base model
Base = declarative_base()

# Ensuring that CSV filesare loaded from a 'data' directory relative to the script
DATA_DIR = os.getenv('DATA_DIR', 'data')


class Company(Base):
    __tablename__ = 'companies'

    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)

    financials = relationship('Financial', back_populates='company', uselist=False, cascade='all, delete-orphan')


class Financial(Base):
    __tablename__ = 'financial'

    ticker = Column(String, ForeignKey('companies.ticker'), primary_key=True)
    ebitda = Column(Float)
    sales = Column(Float)
    net_profit = Column(Float)
    market_price = Column(Float)
    net_debt = Column(Float)
    assets = Column(Float)
    equity = Column(Float)
    cash_equivalents = Column(Float)
    liabilities = Column(Float)

    company = relationship('Company', back_populates='financials')


class DatabaseConnection:
    """
    Class responsible for setting up the SQLite database using SQLAlchemy.
    """

    def __init__(self, db_url=None):
        """
        Initialize the database connection and create tables if the database doesn't exist.

        Args:
            db_url (str): The database URL (default: SQLite database).
        """
        # Setting a relative path for the database
        if db_url is None:
            db_url = f"sqlite:///{os.path.join(os.getcwd(), 'investor.db')}"
        
        self.db_url = db_url
        self.engine = create_engine(db_url)        
        self.Session = sessionmaker(bind=self.engine)  # Session factory
        
        # Checking if the database file already exists
        db_path = self.db_url.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            Base.metadata.create_all(self.engine)
    
    def clear_database(self) -> None:
        """
        Clears the database by deleting all rows from 'Financial' and 'Company' tables. 
        """
        with self.Session() as session:
            try:
                session.query(Financial).delete()
                session.query(Company).delete()
                session.commit()
            except Exception as e:
                session.rollback()
                print(f'Error clearing the database: {e}')
                traceback.print_exc()

    def insert_data(self, force_reload: bool = False) -> None:
        """
        Inserting data from CSV files into the database using SQLAlchemy ORM.

        Args:
            force_reload (bool): If True, the data will be reloaded even if there are companies in the database. 
        """
        
        companies_csv = os.path.join(DATA_DIR, 'companies.csv')
        financial_csv = os.path.join(DATA_DIR, 'financial.csv')
        
        with self.Session() as session:
            if force_reload or session.query(Company).count() == 0:
                try:
                    # Ensure CSV files are present
                    if not os.path.exists(companies_csv) or not os.path.exists(financial_csv):
                        print('CSV files not found. Please ensure that "companies.csv" and "financial.csv" are in the "data" directory.')
                        return
                    
                    # Load data from companies.csv
                    with open(companies_csv, newline='') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            company = Company(
                                ticker=row.get('ticker'),
                                name=row.get('name'),
                                sector=row.get('sector', None)
                            )
                            session.merge(company)

                    # Load data from financial.csv
                    with open(financial_csv, newline='') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            financial = Financial(
                                ticker=row['ticker'],
                                ebitda=float(row.get('ebitda', 0)) if row.get('ebitda') else None,
                                sales=float(row.get('sales', 0)) if row.get('sales') else None,
                                net_profit=float(row.get('net_profit', 0)) if row.get('net_profit') else None,
                                market_price=float(row.get('market_price', 0)) if row.get('market_price') else None,
                                net_debt=float(row.get('net_debt', 0)) if row.get('net_debt') else None,
                                assets=float(row.get('assets', 0)) if row.get('assets') else None,
                                equity=float(row.get('equity', 0)) if row.get('equity') else None,
                                cash_equivalents=float(row.get('cash_equivalents', 0)) if row.get('cash_equivalents') else None,
                                liabilities=float(row.get('liabilities', 0)) if row.get('liabilities') else None
                            )
                            session.merge(financial)

                    session.commit()
                    print('Data inserted successfully!')

                except Exception as e:
                    session.rollback()
                    print(f'Error inserting data: {e}')
                    traceback.print_exc()


class Menu(ABC):
    """
    Abstract base class for menus.
    """
    def __init__(self, title: str, options: Dict[str, str]) -> None:
        """
        Initialize the menu with a title and options.

        Args:
            title (str): The title of the menu.
            options (Dict[str, str]): A dictionary of menu options.
        """
        self.title = title
        self.options = options

    def display(self) -> None:
        """
        Display the menu options.
        """
        print(f'\n{self.title}')
        for key in sorted(self.options.keys()):
            print(f'{key} {self.options[key]}')

    @abstractmethod
    def execute(self) -> None:
        """
        Execute the menu loop. Must be implemented by subclasses.
        """
        pass


class MainMenu(Menu):
    """
    Main menu of the application.
    """
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """
        Initialize the main menu with its options and pass the database connection.

        Args:
            db_connection (DatabaseConnection): The database connection object.
        """
        options = {
            '0': 'Exit',
            '1': 'CRUD operations',
            '2': 'Show top ten companies by criteria'
        }
        super().__init__('MAIN MENU', options)
        self.db_connection = db_connection

    def execute(self) -> None:
        """
        Execute the main menu loop.
        """
        while True:
            self.display()
            choice: str = input('Enter an option:\n')

            if choice == '0':
                print('Have a nice day!')
                break
            elif choice == '1':
                submenu = CrudMenu(self.db_connection)
                submenu.execute()
            elif choice == '2':
                submenu = TopTenMenu(self.db_connection)
                submenu.execute()
            else:
                print('Invalid option!')


class CrudMenu(Menu):
    """
    CRUD operations menu.
    """
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """
        Initialize the CRUD menu with its options and database connection

        Args:
            db_connection (DatabaseConnection): The database connection object.
        """
        options = {
            '0': 'Back',
            '1': 'Create a company',
            '2': 'Read a company',
            '3': 'Update a company',
            '4': 'Delete a company',
            '5': 'List all companies'
        }
        super().__init__('CRUD MENU', options)
        self.db_connection = db_connection
    
    def get_float_input(self, prompt: str) -> float:
        """
        Prompts the user for a float input and handles invalid input.

        Args:
            prompt (str): The prompt message to display.

        Returns:
            float: Tha valid float input entered by the user.
        """
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print('Invalid input, please enter a valid number.')
    
    def create_company(self) -> None:
        """
        Creates a company and populates the 'companies' and 'finanacial' tables with its data
        """
        # Gather company information
        ticker = input("Enter ticker (in the format 'MOON'):\n")
        name =  input("Enter company (in the format 'Moon Corp'):\n")
        sector = input("Enter industries (in the format 'Technology'):\n")
        
        # Gather financial information
        ebitda = self.get_float_input("Enter ebitda (in the format '987654321'):\n")
        sales = self.get_float_input("Enter sales (in the format '987654321'):\n")
        net_profit = self.get_float_input("Enter net profit (in the format '987654321'):\n")
        market_price = self.get_float_input("Enter market price (in the format '987654321'):\n")
        net_debt = self.get_float_input("Enter net debt (in the format '987654321'):\n")
        assets = self.get_float_input("Enter assets (in the format '987654321'):\n")
        equity = self.get_float_input("Enter equity (in the format '987654321'):\n")
        cash_equivalents = self.get_float_input("Enter cash equivalents (in the format '987654321'):\n")
        liabilities = self.get_float_input("Enter liabilities (in the format '987654321'):\n")
        
        with self.db_connection.Session() as session:
            try:
                # Creating a Company object
                company = Company(ticker=ticker, name=name, sector=sector)

                # Creating a Financial object
                financial = Financial(
                    ticker=ticker,
                    ebitda=ebitda,
                    sales=sales,
                    net_profit=net_profit,
                    market_price=market_price,
                    net_debt=net_debt,
                    assets=assets,
                    equity=equity,
                    cash_equivalents=cash_equivalents,
                    liabilities=liabilities
                )

                session.merge(company)
                session.merge(financial)
                session.commit()

                print('Company created successfully!')

            except Exception as e:
                session.rollback()
                print(f'An error occurred: {e}')
                traceback.print_exc()
    
    def company_search(self, session) -> object:
        """
        Reades companies by name and returns the selected company object.
        """
        company_name = input('Enter company name:\n')
        companies = session.query(Company).filter(Company.name.ilike(f'%{company_name}%')).all()
            
        if not companies:
            print('Company not found!')
            return None
            
        for idx, company in enumerate(companies):
            print(f'{idx} {company.name}')
            
        try:
            company_idx = int(input('Enter company number:\n'))
            if company_idx < 0 or company_idx >= len(companies):
                print('Invalid selection')
                return None
        except ValueError:
            print('Invalid input!')
            return None
            
        return companies[company_idx]
    
    def read_company(self) -> None:
        """
        Displayes company financial indicators.
        """        
        with self.db_connection.Session() as session:
            try:
                selected_company = self.company_search(session)
                if not selected_company:
                    return
                
                financial = session.query(Financial).filter(Financial.ticker == selected_company.ticker).first()
                if not financial:
                    print('No financial data found for the selected company!')
                    return

                # Calculation of the company's financial indicators
                try:
                    pe_ratio = financial.market_price / financial.net_profit if financial.net_profit else None
                    ps_ratio = financial.market_price / financial.sales if financial.sales else None
                    pb_ratio = financial.market_price / financial.assets if financial.assets else None
                    nd_ebitda_ratio = financial.net_debt / financial.ebitda if financial.ebitda else None
                    roe_ratio = financial.net_profit / financial.equity if financial.equity else None
                    roa_ratio = financial.net_profit / financial.assets if financial.assets else None
                    la_ratio = financial.liabilities / financial.assets if financial.assets else None
                except ZeroDivisionError:
                    print('Error in calculating ratios due to division by zero.')
                    return    

                # Displaying the company's ticker, name, and financial indicators
                print(f'\n{selected_company.ticker} {selected_company.name}')
                print(f'P/E = {pe_ratio:.2f}' if pe_ratio is not None else 'P/E = None')
                print(f"P/S = {ps_ratio:.2f}" if ps_ratio is not None else "P/S = None")
                print(f"P/B = {pb_ratio:.2f}" if pb_ratio is not None else "P/B = None")
                print(f"ND/EBITDA = {nd_ebitda_ratio:.2f}" if nd_ebitda_ratio is not None else "ND/EBITDA = None")
                print(f"ROE = {roe_ratio:.2f}" if roe_ratio is not None else "ROE = None")
                print(f"ROA = {roa_ratio:.2f}" if roa_ratio is not None else "ROA = None")
                print(f"L/A = {la_ratio:.2f}" if la_ratio is not None else "L/A = None")

            except Exception as e:
                print(f'An error occurred: {e}')
    
    def update_company(self) -> None:
        """
        Updates company financial information.
        """
        with self.db_connection.Session() as session:
            try:
                selected_company = self.company_search(session)
                if not selected_company:
                    return
                
                financial = session.query(Financial).filter(Financial.ticker == selected_company.ticker).first()
                if not financial:
                    print('No financial data found for the selected company!')
                    return

                # Getting company's financial information
                financial.ebitda = self.get_float_input("Enter ebitda (in the format '987654321'):\n")
                financial.sales = self.get_float_input("Enter sales (in the format '987654321'):\n")
                financial.net_profit = self.get_float_input("Enter net profit (in the format '987654321'):\n")
                financial.market_price = self.get_float_input("Enter market price (in the format '987654321'):\n")
                financial.net_debt = self.get_float_input("Enter net debt (in the format '987654321'):\n")
                financial.assets = self.get_float_input("Enter assets (in the format '987654321'):\n")
                financial.equity = self.get_float_input("Enter equity (in the format '987654321'):\n")
                financial.cash_equivalents = self.get_float_input("Enter cash equivalents (in the format '987654321'):\n")
                financial.liabilities = self.get_float_input("Enter liabilities (in the format '987654321'):\n")

                session.commit()
                print('Company updated successfully!')

            except Exception as e:
                session.rollback()
                print(f'An error occurred: {e}')
                traceback.print_exc()
        
    def delete_company(self) -> None:
        """
        Deletes a company.
        """
        with self.db_connection.Session() as session:
            try:
                selected_company = self.company_search(session)
                if not selected_company:
                    return
                
                session.delete(selected_company)
                session.commit()
                print('Company deleted successfully!')

            except Exception as e:
                session.rollback()
                print(f'An error occurred: {e}')
                traceback.print_exc()
    
    def list_companies(self) -> None:
        """
        Lists the companies' ticker, name, and industry, ordered by ticker.
        """
        with self.db_connection.Session() as session:
            try:
                ordered_companies = session.query(Company).order_by(Company.ticker).all()

                if not ordered_companies:
                    print('No companies found!')
                    return

                print('\nCOMPANY LIST')

                for company in ordered_companies:
                    print(f'{company.ticker} {company.name} {company.sector}')

            except Exception as e:
                print(f'An error occurred: {e}')

    def execute(self) -> None:
        """
        Execute the CRUD menu loop.
        """
        while True:
            self.display()
            choice: str = input('Enter an option:\n')

            if choice == '0':
                break
            elif choice == '1':
                self.create_company()
                break
            elif choice == '2':
                self.read_company()
                break
            elif choice == '3':
                self.update_company()
                break
            elif choice == '4':
                self.delete_company()
                break
            elif choice == '5':
                self.list_companies()
                break
            else:
                print('Invalid option!')
                break


class TopTenMenu(Menu):
    """
    Top ten companies menu.
    """
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """
        Initialize the top ten menu with its options and database connection.
        """
        options = {
            '0': 'Back',
            '1': 'List by ND/EBITDA',
            '2': 'List by ROE',
            '3': 'List by ROA'
        }
        super().__init__('TOP TEN MENU', options)
        self.db_connection = db_connection
    
    def calculate_top_ten(self, metric: str) -> None:
        """
        Calculate the top ten companies based on the selected financial metric.

        Args:
            metric (str): The financial metric to rank companies by ('ND/EBITDA', 'ROE', 'ROA').
        """
        with self.db_connection.Session() as session:
            try:
                query = session.query(
                    Financial.ticker,
                    Financial.net_debt,
                    Financial.ebitda,
                    Financial.net_profit,
                    Financial.equity,
                    Financial.assets
                )
                
                if metric == 'ND/EBITDA':
                    results = [
                        (row.ticker, row.net_debt / row.ebitda) 
                        for row in query if row.net_debt and row.ebitda
                    ]
                    header = 'ND/EBITDA'
                
                elif metric == 'ROE':
                    results = [
                        (row.ticker, row.net_profit / row.equity)
                        for row in query if row.net_profit and row.equity
                    ]
                    header = 'ROE'
                    
                elif metric == 'ROA':
                    results = [
                        (row.ticker, row.net_profit / row.assets)
                        for row in query if row.net_profit and row.assets
                    ]
                    header = 'ROA'  
                
                else:
                    print('Invalid metric selected')
                    return
                
                # Sort and limit to top ten results
                results.sort(key=lambda x: x[1], reverse=True)
                print(f'\nTICKER {header}')
                for ticker, value in results[:10]:
                    print(f'{ticker} {value:.2f}'.rstrip('0').rstrip('.'))
                
            except Exception as e:
                print(f'Error calculationg {metric}: {e}')
                traceback.print_exc()
        
    def execute(self) -> None:
        """
        Execute the top ten menu loop.
        """
        while True:
            self.display()
            choice: str = input('Enter an option:\n')

            if choice == '0':
                break
            elif choice == '1':
                self.calculate_top_ten('ND/EBITDA')
                break
            elif choice == '2':
                self.calculate_top_ten('ROE')
                break
            elif choice == '3':
                self.calculate_top_ten('ROA')
                break
            else:
                print('Invalid option!')
                break


class MenuManager:
    """
    Manages the execution of menus.
    """
    def __init__(self, db_connection: DatabaseConnection) -> None:
        """
        Initializes the MenuManager with the main menu.

        Args:
            db_connection (DatabaseConnection): The database connection object.
        """
        self.current_menu = MainMenu(db_connection)

    def run(self) -> None:
        """
        Run the current menu.
        """
        self.current_menu.execute()


if __name__ == '__main__':
    print('Welcome to the Investor Program!')
    
    # Database set-up and data insertion
    db_connection = DatabaseConnection()
    db_connection.insert_data()

    # Running the menu system
    menu_manager = MenuManager(db_connection)
    menu_manager.run()