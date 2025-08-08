import pandas as pd
import numpy as np
try:
    import talib as ta
except ImportError:
    import pandas_ta as ta

class TradingStrategy:
    def __init__(self, tp_percent=2.0, sl_percent=1.0, rsi_period=14, ma_period=20):
        self.tp_percent = tp_percent
        self.sl_percent = sl_percent
        self.rsi_period = rsi_period
        self.ma_period = ma_period
    
    def calculate_indicators(self, df):
        # Simple RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Moving averages
        df['ma'] = df['close'].rolling(window=self.ma_period).mean()
        df['ema_fast'] = df['close'].ewm(span=12).mean()
        df['ema_slow'] = df['close'].ewm(span=26).mean()
        return df
    
    def generate_signals(self, df):
        df = self.calculate_indicators(df)
        signals = []
        
        for i in range(1, len(df)):
            # Long signal: RSI oversold + EMA crossover + price above MA
            if (df['rsi'].iloc[i] < 30 and 
                df['ema_fast'].iloc[i] > df['ema_slow'].iloc[i] and
                df['ema_fast'].iloc[i-1] <= df['ema_slow'].iloc[i-1] and
                df['close'].iloc[i] > df['ma'].iloc[i]):
                
                signals.append({
                    'timestamp': df.index[i],
                    'side': 'long',
                    'price': df['close'].iloc[i],
                    'tp_price': df['close'].iloc[i] * (1 + self.tp_percent/100),
                    'sl_price': df['close'].iloc[i] * (1 - self.sl_percent/100)
                })
            
            # Short signal: RSI overbought + EMA crossover + price below MA
            elif (df['rsi'].iloc[i] > 70 and 
                  df['ema_fast'].iloc[i] < df['ema_slow'].iloc[i] and
                  df['ema_fast'].iloc[i-1] >= df['ema_slow'].iloc[i-1] and
                  df['close'].iloc[i] < df['ma'].iloc[i]):
                
                signals.append({
                    'timestamp': df.index[i],
                    'side': 'short',
                    'price': df['close'].iloc[i],
                    'tp_price': df['close'].iloc[i] * (1 - self.tp_percent/100),
                    'sl_price': df['close'].iloc[i] * (1 + self.sl_percent/100)
                })
        
        return signals
    
    def backtest_strategy(self, df, initial_balance=1000, leverage=10):
        signals = self.generate_signals(df)
        trades = []
        balance = initial_balance
        position = None
        
        for signal in signals:
            if position is None:  # No open position
                position = {
                    'side': signal['side'],
                    'entry_price': signal['price'],
                    'tp_price': signal['tp_price'],
                    'sl_price': signal['sl_price'],
                    'size': balance * leverage / signal['price'],
                    'entry_time': signal['timestamp']
                }
            else:
                # Check if we should close position
                current_price = signal['price']
                
                if position['side'] == 'long':
                    if current_price >= position['tp_price'] or current_price <= position['sl_price']:
                        pnl = (current_price - position['entry_price']) * position['size']
                        balance += pnl
                        
                        trades.append({
                            'entry_time': position['entry_time'],
                            'exit_time': signal['timestamp'],
                            'side': position['side'],
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'pnl': pnl,
                            'balance': balance
                        })
                        position = None
                
                elif position['side'] == 'short':
                    if current_price <= position['tp_price'] or current_price >= position['sl_price']:
                        pnl = (position['entry_price'] - current_price) * position['size']
                        balance += pnl
                        
                        trades.append({
                            'entry_time': position['entry_time'],
                            'exit_time': signal['timestamp'],
                            'side': position['side'],
                            'entry_price': position['entry_price'],
                            'exit_price': current_price,
                            'pnl': pnl,
                            'balance': balance
                        })
                        position = None
        
        return trades, balance

class ParameterOptimizer:
    def __init__(self, df):
        self.df = df
    
    def optimize(self, param_ranges):
        best_params = None
        best_profit = -float('inf')
        
        tp_range = param_ranges.get('tp_percent', [1.0, 2.0, 3.0, 4.0, 5.0])
        sl_range = param_ranges.get('sl_percent', [0.5, 1.0, 1.5, 2.0])
        rsi_range = param_ranges.get('rsi_period', [10, 14, 18, 22])
        ma_range = param_ranges.get('ma_period', [15, 20, 25, 30])
        
        for tp in tp_range:
            for sl in sl_range:
                for rsi in rsi_range:
                    for ma in ma_range:
                        strategy = TradingStrategy(tp, sl, rsi, ma)
                        trades, final_balance = strategy.backtest_strategy(self.df)
                        
                        if len(trades) > 5:  # Minimum trades required
                            profit = final_balance - 1000
                            win_rate = len([t for t in trades if t['pnl'] > 0]) / len(trades)
                            
                            if profit > best_profit and win_rate > 0.6:
                                best_profit = profit
                                best_params = {
                                    'tp_percentage': tp,
                                    'sl_percentage': sl,
                                    'rsi_period': rsi,
                                    'ma_period': ma,
                                    'expected_profit': profit,
                                    'win_rate': win_rate
                                }
        
        return best_params or {
            'tp_percentage': 2.0,
            'sl_percentage': 1.0,
            'rsi_period': 14,
            'ma_period': 20
        }