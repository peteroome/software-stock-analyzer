from src.analyzer import CompleteStockAnalyzer

def detailed_analysis(ticker):
    analyzer = CompleteStockAnalyzer()
    result = analyzer.analyze_stock(ticker)
    
    if result and 'composite_score' in result:
        print(f"\nDetailed Analysis for {result['ticker']}:")
        print(f"Overall Score: {result['composite_score']:.1f}")
        print(f"Rating: {result['rating']}")
        print("\nComponent Scores:")
        for name, score in result['component_scores'].items():
            print(f"{name}: {score:.1f}")
        print("\nKey Metrics:")
        for name, value in result['key_metrics'].items():
            if isinstance(value, float):
                print(f"{name}: {value:.1f}")
            else:
                print(f"{name}: {value}")
    else:
        print("Analysis failed or returned unexpected result")

if __name__ == "__main__":
    detailed_analysis('DDOG')