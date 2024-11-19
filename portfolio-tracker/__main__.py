import os
import sys
import pandas as pd
import yfinance as yf
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.padding import Padding

console = Console()

DATE_FORMAT = '%d-%m-%Y %H:%M'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPERATIONS_FILE = os.path.join(BASE_DIR, 'db', 'operations.csv')
PORTFOLIO_FILE = os.path.join(BASE_DIR, 'db', 'portfolio.csv')

def read_dbs():
    try:
        portfolio = pd.read_csv(PORTFOLIO_FILE)
        operations = pd.read_csv(OPERATIONS_FILE)
    except FileNotFoundError as e:
        console.print(f"Error: {e}")
        portfolio = pd.DataFrame(columns=['symbol', 'position'])
        operations = pd.DataFrame(
            columns=['operation', 'position', 'symbol', 'price', 'currency', 'date'])
    return portfolio, operations


def save_dbs(operations, portfolio):
    operations.to_csv(OPERATIONS_FILE, index=False)
    portfolio.to_csv(PORTFOLIO_FILE, index=False)

def format_float(value):
    return f"{value:,.1f}" if value % 1 != 0 else f"{value:,.0f}"

def print_report(operations, portfolio):
    table = Table(title='Current Portfolio')
    table.add_column('SYMBOL', justify='left')
    table.add_column('POSITION', justify='right')
    table.add_column('AVG PRICE', justify='right')
    table.add_column('COST BASIS', justify='right')
    table.add_column('MARKET VALUE', justify='right')
    table.add_column('UNREALIZED P&L', justify='right')

    for _, row in portfolio.iterrows():
        symbol = row['symbol']
        condition = (operations['symbol'] == symbol) & (operations['operation'] == 'add')
        avg_price = operations.loc[condition, 'price'].mean()
        cost_basis = (operations.loc[condition, 'position'] * operations.loc[condition, 'price']).sum()
        currency = operations.loc[condition, 'currency'].values[0]

        if currency == 'ARS':
            symbol_for_yf = f'{symbol}.BA'
        else:
            symbol_for_yf = symbol[:-1] if symbol.endswith('D') else symbol

        closing_price = get_latest_closing_price(symbol_for_yf)

        avg_price_str = f'{format_float(avg_price)} {currency}'
        cost_basis_str = f'{format_float(cost_basis)} {currency}'
        position_str = format_float(row['position'])
        market_value_str = f'{format_float(closing_price * row["position"])} {currency}' if closing_price else '---'

        if closing_price:
            unrealized_pl = (closing_price - avg_price) * row['position']
            unrealized_pl_str = f'{format_float(unrealized_pl)} {currency}'
            if unrealized_pl > 0:
                unrealized_pl_str = f'[green]{unrealized_pl_str}[/green]'
            elif unrealized_pl < 0:
                unrealized_pl_str = f'[red]{unrealized_pl_str}[/red]'
        else:
            unrealized_pl_str = '---'

        table.add_row(symbol, position_str, avg_price_str, cost_basis_str, market_value_str, unrealized_pl_str)

    padding = Padding("", (1, 0), expand=True)
    console.print(padding)
    console.print(table)
    console.print(padding)


def validate_args(args):
    if len(args) < 5:
        raise ValueError("Insufficient arguments provided.")
    verb = args[0]
    position = float(args[1])
    symbol = args[2]
    price = float(args[3])
    currency = args[4]
    return verb, position, symbol, price, currency


def update_portfolio(portfolio, verb, symbol, position):
    if len(portfolio.loc[portfolio['symbol'] == symbol]) == 0:
        console.print(f'{symbol} not found in db. Adding {symbol} to db...')
        portfolio = pd.concat([portfolio, pd.DataFrame(
            {'symbol': [symbol], 'position': [position]})], ignore_index=True)
    else:
        if verb == 'add':
            portfolio.loc[portfolio['symbol'] ==
                          symbol, 'position'] += position
        elif verb == 'sub':
            portfolio.loc[portfolio['symbol'] ==
                          symbol, 'position'] -= position
        elif verb == 'reset':
            portfolio.loc[portfolio['symbol'] == symbol, 'position'] = position
    return portfolio


def add_operation(operations, verb, position, symbol, price, currency):
    console.print(
        f'Adding operation: {verb} {position} {symbol} at {price} {currency}...')
    new_row = pd.DataFrame({
        'operation': [verb],
        'position': [position],
        'symbol': [symbol],
        'price': [price],
        'currency': [currency],
        'date': [datetime.now().strftime(DATE_FORMAT)]
    }).dropna(how='all')

    if not new_row.empty:
        operations = pd.concat([operations, new_row], ignore_index=True)
    return operations


def main():
    args = sys.argv[1:]
    portfolio, operations = read_dbs()

    if args[0] == 'report':
        print_report(operations, portfolio)
        return

    try:
        verb, position, symbol, price, currency = validate_args(args)
    except ValueError as e:
        console.print(f"Error: {e}")
        return

    portfolio = update_portfolio(portfolio, verb, symbol, position)
    operations = add_operation(
        operations, verb, symbol, position, price, currency)
    save_dbs(operations, portfolio)

def get_latest_closing_price(symbol):
      stock = yf.Ticker(symbol)
      hist = stock.history(period="1d")
      if not hist.empty:
          return hist['Close'].iloc[-1]
      else:
          return None

if __name__ == '__main__':
    main()