import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .constants import load_universe

class CompleteStockAnalyzer:
    def __init__(self):
        self.universe = load_universe()
        # Add these lines:
        self.min_market_cap = 1_000_000_000  # $1B
        self.max_market_cap = 70_000_000_000  # $70B

    def analyze_universe(self):
        """Analyze all stocks in the universe"""
        results = []
        total_stocks = len(self.universe)
        
        for idx, row in self.universe.iterrows():
            ticker = row['ticker']
            print(f"Analyzing {ticker} ({idx+1}/{total_stocks})")
            
            analysis = self.analyze_stock(ticker)
            if analysis and 'composite_score' in analysis:
                results.append(analysis)
        
        return sorted(results, key=lambda x: x['composite_score'], reverse=True)

    def get_rating(self, score):
        """Convert numerical score to rating"""
        if score >= 90: return "Strong Buy"
        elif score >= 80: return "Buy"
        elif score >= 70: return "Accumulate"
        elif score >= 60: return "Hold"
        elif score >= 50: return "Reduce"
        else: return "Sell"

    def calculate_growth_value_score(self, stock):
        """Calculate growth and value metrics"""
        info = stock.info
        
        # Basic metrics
        ps_ratio = info.get('priceToSalesTrailing12Months', 0)
        revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
        gross_margins = info.get('grossMargins', 0) * 100 if info.get('grossMargins') else 0
        
        # Growth score
        growth_score = min(100, max(0, revenue_growth * 2))
        
        # Value-Growth Alignment
        growth_justified_ps = revenue_growth * 0.5
        alignment_score = min(100, max(0, 100 * (growth_justified_ps / max(ps_ratio, 1))))
        
        # Margin score
        margin_score = min(100, max(0, gross_margins * 1.25))
        
        return {
            'growth_score': growth_score,
            'alignment_score': alignment_score,
            'margin_score': margin_score,
            'metrics': {
                'ps_ratio': ps_ratio,
                'revenue_growth': revenue_growth,
                'gross_margins': gross_margins
            }
        }

    def calculate_business_health(self, stock):
        """Calculate financial health and insider confidence"""
        info = stock.info
        
        # Financial health
        current_ratio = info.get('currentRatio', 1)
        debt_to_equity = info.get('debtToEquity', 0)
        cash_to_debt = info.get('totalCash', 0) / max(info.get('totalDebt', 1), 1)
        
        financial_score = min(100, max(0,
            30 * min(2, current_ratio) +
            40 * min(1, cash_to_debt) +
            30 * (1 - min(1, debt_to_equity/100))
        ))
        
        # Insider confidence
        insider_percent = info.get('heldPercentInsiders', 0) * 100
        inst_percent = info.get('heldPercentInstitutions', 0) * 100
        
        insider_score = min(100, max(0,
            50 * min(1, insider_percent/20) +
            50 * min(1, inst_percent/70)
        ))
        
        return {
            'financial_score': financial_score,
            'insider_score': insider_score,
            'metrics': {
                'current_ratio': current_ratio,
                'cash_to_debt': cash_to_debt,
                'insider_ownership': insider_percent,
                'institutional_ownership': inst_percent
            }
        }

    def calculate_market_validation(self, stock):
        """Calculate momentum and volume trends"""
        hist = stock.history(period='200d')
        if len(hist) < 200:  # Handle cases with insufficient history
            return {
                'momentum_score': 50,
                'volume_score': 50,
                'metrics': {
                    'price_vs_ma50': 0,
                    'price_vs_ma200': 0,
                    'volume_trend': 1
                }
            }
        
        # Momentum - using iloc instead of [] for position-based indexing
        current_price = hist['Close'].iloc[-1]
        ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        momentum_score = 0
        if current_price > ma50: momentum_score += 40
        if current_price > ma200: momentum_score += 40
        if ma50 > ma200: momentum_score += 20
        
        # Volume trends - also using iloc for volumes
        recent_volume = hist['Volume'].iloc[-20:].mean()
        old_volume = hist['Volume'].iloc[-50:-20].mean()
        volume_trend = recent_volume / old_volume if old_volume > 0 else 1
        
        volume_score = min(100, max(0, 50 * volume_trend))
        
        return {
            'momentum_score': momentum_score,
            'volume_score': volume_score,
            'metrics': {
                'price_vs_ma50': (current_price/ma50 - 1) * 100 if ma50 > 0 else 0,
                'price_vs_ma200': (current_price/ma200 - 1) * 100 if ma200 > 0 else 0,
                'volume_trend': volume_trend
            }
        }

    def analyze_stock(self, ticker):
        """Complete stock analysis"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check market cap range
            market_cap = info.get('marketCap', 0)
            if market_cap < self.min_market_cap or market_cap > self.max_market_cap:
                return None
                
            # Calculate all components
            growth_value = self.calculate_growth_value_score(stock)
            business = self.calculate_business_health(stock)
            market = self.calculate_market_validation(stock)
            
            # Calculate final composite score
            composite_score = (
                0.20 * growth_value['growth_score'] +      # Growth
                0.20 * growth_value['alignment_score'] +   # Value-Growth Alignment
                0.10 * growth_value['margin_score'] +      # Margins
                0.15 * business['financial_score'] +       # Financial Health
                0.15 * business['insider_score'] +         # Insider Confidence
                0.10 * market['momentum_score'] +          # Momentum
                0.10 * market['volume_score']              # Volume Trends
            )
            
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'market_cap': market_cap / 1e9,
                'composite_score': composite_score,
                'rating': self.get_rating(composite_score),
                'component_scores': {
                    'growth': growth_value['growth_score'],
                    'value_alignment': growth_value['alignment_score'],
                    'margins': growth_value['margin_score'],
                    'financial_health': business['financial_score'],
                    'insider_confidence': business['insider_score'],
                    'momentum': market['momentum_score'],
                    'volume_trends': market['volume_score']
                },
                'key_metrics': {
                    **growth_value['metrics'],
                    **business['metrics'],
                    **market['metrics']
                }
            }
            
        except Exception as e:
            return {'ticker': ticker, 'error': str(e)}

    def scan_multiple_stocks(self, tickers):
        """
        Analyze multiple stocks and return sorted results
        """
        results = []
        for ticker in tickers:
            analysis = self.analyze_stock(ticker)
            if analysis and 'composite_score' in analysis:
                results.append(analysis)
        
        # Sort by composite score
        return sorted(results, key=lambda x: x['composite_score'], reverse=True)