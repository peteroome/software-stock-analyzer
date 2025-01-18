import pytest
from src.analyzer import CompleteStockAnalyzer
import pandas as pd

def format_score_output(name, value, indent=0):
    """Helper function to format score outputs"""
    spaces = " " * indent
    return f"{spaces}{name}: {value:.1f}"

def test_known_stock_values(ticker='DDOG'):
    """Test complete analysis of a known stock"""
    analyzer = CompleteStockAnalyzer()
    stock = analyzer.analyze_stock(ticker)
    
    if not stock or 'error' in stock:
        print(f"\nError analyzing {ticker}: {stock.get('error', 'Unknown error')}")
        return
    
    print(f"\n{'='*20} Stock Analysis: {ticker} {'='*20}")
    
    # Basic Info
    print(f"\nBasic Information:")
    print(f"Company: {stock['name']}")
    print(f"Market Cap: ${stock['market_cap']:.1f}B")
    print(f"Overall Score: {stock['composite_score']:.1f}")
    print(f"Rating: {stock['rating']}")
    
    # Component Scores
    print("\nComponent Scores:")
    for name, score in stock['component_scores'].items():
        print(format_score_output(name.replace('_', ' ').title(), score, indent=2))
    
    # Weighted Contributions
    print("\nWeighted Score Contributions:")
    weights = {
        'growth': 0.20,
        'value_alignment': 0.20,
        'margins': 0.10,
        'financial_health': 0.15,
        'insider_confidence': 0.15,
        'momentum': 0.10,
        'volume_trends': 0.10
    }
    
    weighted_sum = 0
    for name, score in stock['component_scores'].items():
        weighted_score = score * weights[name]
        weighted_sum += weighted_score
        print(format_score_output(
            f"{name.replace('_', ' ').title()} ({weights[name]*100}%)", 
            weighted_score, 
            indent=2
        ))
    
    print(f"\nTotal from weighted components: {weighted_sum:.1f}")
    print(f"Reported composite score: {stock['composite_score']:.1f}")
    
    if abs(weighted_sum - stock['composite_score']) > 0.1:
        print("WARNING: Weighted sum doesn't match composite score!")
    
    # Key Metrics
    print("\nKey Metrics:")
    for name, value in stock['key_metrics'].items():
        if isinstance(value, float):
            print(f"  {name}: {value:.1f}")
        else:
            print(f"  {name}: {value}")

def test_edge_cases():
    """Test scoring system with edge case scenarios"""
    class MockStock:
        def __init__(self, info, history_data=None):
            self.info = info
            self._history = history_data
            
        def history(self, period):
            if self._history is not None:
                return self._history
            return pd.DataFrame()  # Return empty DataFrame if no history provided
    
    print("\n" + "="*20 + " Edge Case Testing " + "="*20)
    
    edge_cases = [
        {
            'name': 'High Growth Tech',
            'info': {
                'marketCap': 5_000_000_000,
                'revenueGrowth': 0.80,  # 80% growth
                'grossMargins': 0.85,    # 85% margins
                'priceToSalesTrailing12Months': 20,
                'currentRatio': 3,
                'debtToEquity': 10,
                'totalCash': 1_000_000_000,
                'totalDebt': 100_000_000,
                'heldPercentInsiders': 0.15,
                'heldPercentInstitutions': 0.80
            }
        },
        {
            'name': 'Value Trap',
            'info': {
                'marketCap': 2_000_000_000,
                'revenueGrowth': 0.05,   # 5% growth
                'grossMargins': 0.40,     # 40% margins
                'priceToSalesTrailing12Months': 2,
                'currentRatio': 1.1,
                'debtToEquity': 80,
                'totalCash': 100_000_000,
                'totalDebt': 500_000_000,
                'heldPercentInsiders': 0.05,
                'heldPercentInstitutions': 0.40
            }
        },
        {
            'name': 'Balanced Growth',
            'info': {
                'marketCap': 10_000_000_000,
                'revenueGrowth': 0.30,    # 30% growth
                'grossMargins': 0.70,      # 70% margins
                'priceToSalesTrailing12Months': 10,
                'currentRatio': 2,
                'debtToEquity': 30,
                'totalCash': 500_000_000,
                'totalDebt': 300_000_000,
                'heldPercentInsiders': 0.10,
                'heldPercentInstitutions': 0.65
            }
        }
    ]
    
    analyzer = CompleteStockAnalyzer()
    
    for case in edge_cases:
        mock_stock = MockStock(case['info'])
        print(f"\nTesting {case['name']}:")
        
        # Calculate scores
        growth_value = analyzer.calculate_growth_value_score(mock_stock)
        business = analyzer.calculate_business_health(mock_stock)
        
        print(f"\nGrowth & Value Metrics:")
        for key, value in growth_value['metrics'].items():
            print(f"  {key}: {value:.1f}")
        
        print(f"\nScores:")
        print(f"  Growth Score: {growth_value['growth_score']:.1f}")
        print(f"  Value Alignment Score: {growth_value['alignment_score']:.1f}")
        print(f"  Margin Score: {growth_value['margin_score']:.1f}")
        print(f"  Financial Health Score: {business['financial_score']:.1f}")
        print(f"  Insider Confidence Score: {business['insider_score']:.1f}")

def validate_calculations():
    """Validate specific calculation steps"""
    analyzer = CompleteStockAnalyzer()
    
    print("\n" + "="*20 + " Calculation Validation " + "="*20)
    
    # Test growth score calculation
    test_growth = 0.35  # 35% growth
    expected_growth_score = min(100, max(0, test_growth * 100 * 2))
    
    print(f"\nGrowth Score Validation:")
    print(f"Input Growth Rate: {test_growth*100}%")
    print(f"Expected Score: {expected_growth_score}")
    
    # Test margin score calculation
    test_margin = 0.75  # 75% margin
    expected_margin_score = min(100, max(0, test_margin * 100 * 1.25))
    
    print(f"\nMargin Score Validation:")
    print(f"Input Margin: {test_margin*100}%")
    print(f"Expected Score: {expected_margin_score}")

if __name__ == "__main__":
    print("\nRunning Scoring System Validation Tests")
    print("=" * 50)
    
    # Test real stock
    test_known_stock_values('DDOG')
    
    # Test edge cases
    test_edge_cases()
    
    # Validate calculations
    validate_calculations()