"""Backtesting engine for testing trading strategies on historical data"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class Backtester:
    """
    Backtesting framework that simulates trading and calculates performance metrics
    
    Features:
    - Realistic trade simulation (slippage, commissions)
    - Portfolio tracking over time
    - Comprehensive performance metrics
    - Multi-strategy comparison
    """
    
    def __init__(self, initial_capital=10000, commission=0.001, slippage=0.0005):
        """
        Initialize backtester with trading parameters
        
        Args:
            initial_capital: Starting portfolio value in dollars
            commission: Commission per trade as percentage (0.001 = 0.1%)
            slippage: Price slippage as percentage (0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital
        self.commission = commission  # Trading fee per trade
        self.slippage = slippage  # Price impact when entering/exiting
    
    def run_backtest(self, strategy, df: pd.DataFrame) -> Dict:
        """
        Run backtest for a single strategy on historical data
        
        Args:
            strategy: Trading strategy object with generate_signals() method
            df: DataFrame with OHLCV data
        
        Returns:
            Dictionary with:
            - trades: List of all trades executed
            - equity_curve: Portfolio value over time
            - metrics: Performance metrics dictionary
        """
        
        # Generate trading signals
        df = strategy.generate_signals(df)
        
        # Initialize tracking variables
        portfolio_value = self.initial_capital  # Current portfolio value
        cash = self.initial_capital  # Available cash
        position = 0  # Current position size (0 = no position)
        trades = []  # List of completed trades
        equity_curve = []  # Portfolio value at each timestamp
        
        # Track entry price for open positions
        entry_price = 0
        entry_time = None
        
        # Simulate trading through each bar
        for timestamp, row in df.iterrows():
            
            # Get current signal
            if pd.notna(row['signal']):
                current_signal = row['signal']
                
                # BUY SIGNAL (1) - enter long position
                if current_signal == 1 and position == 0:
                    buy_price = row['close'] * (1 + self.slippage)
                    commission_cost = cash * self.commission
                    shares = (cash - commission_cost) / buy_price
                    position = shares
                    cash = 0
                    entry_price = buy_price
                    entry_time = timestamp
                
                # SELL SIGNAL (-1) OR HOLD (0) - exit if we have position
                elif (current_signal == -1 or current_signal == 0) and position > 0:
                    sell_price = row['close'] * (1 - self.slippage)
                    sale_proceeds = position * sell_price
                    commission_cost = sale_proceeds * self.commission
                    cash = sale_proceeds - commission_cost
                    
                    trade_return = ((sell_price - entry_price) / entry_price) * 100
                    
                    trades.append({
                        'entry_time': entry_time,
                        'exit_time': timestamp,
                        'entry_price': entry_price,
                        'exit_price': sell_price,
                        'shares': position,
                        'return_pct': trade_return,
                        'pnl': (sell_price - entry_price) * position - (commission_cost * 2)
                    })
                    
                    position = 0
                    entry_price = 0
                    entry_time = None
            
            # Calculate current portfolio value
            if position > 0:
                # If holding position, value = cash + position value
                portfolio_value = cash + (position * row['close'])
            else:
                # If no position, value = cash only
                portfolio_value = cash
            
            # Record portfolio value at this timestamp
            equity_curve.append({
                'timestamp': timestamp,
                'portfolio_value': portfolio_value
            })
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(trades, equity_curve)
        
        # Return results
        return {
            'strategy_name': strategy.name,
            'trades': trades,
            'equity_curve': pd.DataFrame(equity_curve),
            'metrics': metrics
        }
    
    def _calculate_metrics(self, trades: List[Dict], equity_curve: List[Dict]) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades: List of trade dictionaries
            equity_curve: List of portfolio values over time
        
        Returns:
            Dictionary of performance metrics
        """
        
        # Convert equity curve to DataFrame for easier calculations
        equity_df = pd.DataFrame(equity_curve)
        
        # Handle case with no trades
        if len(trades) == 0:
            return {
                'total_return': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'final_portfolio_value': self.initial_capital
            }
        
        # Calculate basic metrics
        final_value = equity_df['portfolio_value'].iloc[-1]
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Trade statistics
        winning_trades = [t for t in trades if t['return_pct'] > 0]
        losing_trades = [t for t in trades if t['return_pct'] <= 0]
        
        total_trades = len(trades)
        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        win_rate = (num_wins / total_trades * 100) if total_trades > 0 else 0
        
        # Average win/loss
        avg_win = np.mean([t['return_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['return_pct'] for t in losing_trades]) if losing_trades else 0
        
        # Profit factor (total wins / total losses)
        total_wins = sum([t['pnl'] for t in winning_trades]) if winning_trades else 0
        total_losses = abs(sum([t['pnl'] for t in losing_trades])) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses != 0 else 0
        
        # Calculate max drawdown (worst peak-to-trough decline)
        equity_df['cummax'] = equity_df['portfolio_value'].cummax()  # Running maximum
        equity_df['drawdown'] = (equity_df['portfolio_value'] - equity_df['cummax']) / equity_df['cummax'] * 100
        max_drawdown = equity_df['drawdown'].min()  # Most negative drawdown
        
        # Calculate Sharpe ratio (risk-adjusted return)
        # First calculate returns between each timestamp
        equity_df['returns'] = equity_df['portfolio_value'].pct_change()
        
        # Sharpe = (mean return - risk free rate) / std deviation of returns
        # Assuming 0% risk-free rate for simplicity
        mean_return = equity_df['returns'].mean()
        std_return = equity_df['returns'].std()
        
        # Annualize Sharpe ratio (assuming daily data, 252 trading days/year)
        periods_per_year = 252  # For daily data
        sharpe_ratio = (mean_return / std_return) * np.sqrt(periods_per_year) if std_return != 0 else 0
        
        # Return all metrics
        return {
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': num_wins,
            'losing_trades': num_losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_portfolio_value': final_value
        }
    
    def compare_strategies(self, strategies: List, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run multiple strategies on same data and compare results
        
        Args:
            strategies: List of strategy objects
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame comparing all strategies' performance
        """
        
        results = []
        
        # Run backtest for each strategy
        for strategy in strategies:
            print(f"Testing {strategy.name}...")
            
            # Run backtest
            result = self.run_backtest(strategy, df.copy())
            
            # Extract metrics
            metrics = result['metrics']
            metrics['strategy'] = strategy.name
            
            results.append(metrics)
        
        # Convert to DataFrame for easy comparison
        comparison_df = pd.DataFrame(results)
        
        # Reorder columns to put strategy name first
        cols = ['strategy'] + [col for col in comparison_df.columns if col != 'strategy']
        comparison_df = comparison_df[cols]
        
        return comparison_df