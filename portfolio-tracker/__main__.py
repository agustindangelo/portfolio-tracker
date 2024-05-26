import sys
import sys
import pandas as pd
import pandas as pd

from rich.table import Table
from rich.padding import Padding
from rich.console import Console

console = Console()

# from .classmodule import MyClass
# from .funcmodule import my_function

def read_db():
  portfolio = pd.read_csv('./db/portfolio.csv')
  return portfolio
 
def validate_args(args):
  if len(args) != 3:
    raise Exception('Usage error. Pass arguments <verb> <symbol> <quantity>')
  verb = args[0]
  symbol = args[1]
  quantity = args[2]

  if verb not in ('add', 'sub', 'reset'):
    raise Exception(f'Unknown verb {verb}')

  try:
    quantity = float(quantity)
  except:
    raise Exception(f'Quantity must be a number')

  return verb, symbol, quantity

def save_db(df):
  df.to_csv('./db/portfolio.csv', index=False)

def print_report(df):
  table = Table(title=f'Portfolio')

  table.add_column('SYMBOL', justify='left')
  table.add_column('QUANTITY', justify='right')

  for row in df.iterrows():
    table.add_row(row[1]['symbol'], str(row[1]['quantity']))

  padding = Padding("", (1, 0), expand=True)
  console.print(padding)
  console.print(table)
  console.print(padding)

def main():
  args = sys.argv[1:]
  df = read_db() 

  if args[0] == 'report':
    print_report(df)
    return
  
  verb, symbol, quantity = validate_args(args)

  if len(df.loc[df['symbol'] == symbol]) == 0:
    print(f'{symbol} not found in db. Adding {symbol} to db...')
    df = pd.concat([df, pd.DataFrame({'symbol': [symbol], 'quantity': [quantity]})], ignore_index = True)
  else:
    if verb == 'add':
      df.loc[df['symbol'] == symbol, 'quantity'] += quantity
      print(f'Added {quantity} of {symbol} to db...')
    elif verb == 'sub':
      df.loc[df['symbol'] == symbol, 'quantity'] -= quantity
      print(f'Removed {quantity} of {symbol} from db...')
    elif verb == 'reset':
      df.loc[df['symbol'] == symbol, 'quantity'] = quantity
      print(f'Reseted {symbol} to {quantity} in db...')
    
  save_db(df)

if __name__ == '__main__':
    main()