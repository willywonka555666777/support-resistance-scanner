import sqlite3
from datetime import datetime
import json

class TradingDatabase:
    def __init__(self, db_path='trading.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                tp_price REAL,
                sl_price REAL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                entry_time DATETIME,
                exit_time DATETIME,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                pnl REAL,
                status TEXT DEFAULT 'open',
                FOREIGN KEY (signal_id) REFERENCES signals (id)
            )
        ''')
        
        # Backtest results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                initial_balance REAL,
                final_balance REAL,
                total_trades INTEGER,
                win_rate REAL,
                parameters TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_signal(self, symbol, side, price, tp_price=None, sl_price=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (symbol, side, price, tp_price, sl_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, side, price, tp_price, sl_price))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return signal_id
    
    def save_trade(self, signal_id, symbol, side, entry_price, quantity, entry_time=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if entry_time is None:
            entry_time = datetime.now()
        
        cursor.execute('''
            INSERT INTO trades (signal_id, symbol, side, entry_price, quantity, entry_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (signal_id, symbol, side, entry_price, quantity, entry_time))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trade_id
    
    def close_trade(self, trade_id, exit_price, exit_time=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if exit_time is None:
            exit_time = datetime.now()
        
        # Get trade details to calculate PnL
        cursor.execute('SELECT side, entry_price, quantity FROM trades WHERE id = ?', (trade_id,))
        trade = cursor.fetchone()
        
        if trade:
            side, entry_price, quantity = trade
            if side == 'long':
                pnl = (exit_price - entry_price) * quantity
            else:
                pnl = (entry_price - exit_price) * quantity
            
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, exit_time = ?, pnl = ?, status = 'closed'
                WHERE id = ?
            ''', (exit_price, exit_time, pnl, trade_id))
        
        conn.commit()
        conn.close()
    
    def save_backtest_result(self, symbol, start_date, end_date, initial_balance, 
                           final_balance, total_trades, win_rate, parameters):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backtest_results 
            (symbol, start_date, end_date, initial_balance, final_balance, 
             total_trades, win_rate, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, start_date, end_date, initial_balance, final_balance,
              total_trades, win_rate, json.dumps(parameters)))
        
        conn.commit()
        conn.close()
    
    def get_recent_signals(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, symbol, side, price, status
            FROM signals
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        signals = cursor.fetchall()
        conn.close()
        return signals
    
    def get_trade_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE status = 'closed'
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats and stats[0] > 0:
            return {
                'total_trades': stats[0],
                'winning_trades': stats[1],
                'win_rate': (stats[1] / stats[0]) * 100,
                'total_pnl': stats[2],
                'avg_pnl': stats[3]
            }
        return None