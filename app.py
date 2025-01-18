# app.py
import streamlit as st
from src.analyzer import CompleteStockAnalyzer
from src.constants import load_universe

def main():
    st.title("Software Stock Analyzer")
    
    # Load universe
    universe = load_universe()
    
    # Sidebar controls
    st.sidebar.header("Analysis Controls")
    
    # Universe stats
    st.sidebar.subheader("Universe Statistics")
    st.sidebar.write(f"Total Stocks: {len(universe)}")
    
    # Stock selection
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks to Analyze",
        universe['ticker'].tolist(),
        default=universe['ticker'].head(3).tolist()
    )
    
    # Run analysis button
    if st.sidebar.button("Run Analysis"):
        analyzer = CompleteStockAnalyzer()
        results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        for i, ticker in enumerate(selected_stocks):
            result = analyzer.analyze_stock(ticker)
            if result and 'composite_score' in result:
                results.append(result)
            progress_bar.progress((i + 1) / len(selected_stocks))
        
        # Display results
        if results:
            display_results(results)

def display_results(results):
    # Convert to DataFrame for easier display
    df = pd.DataFrame(results)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Score", f"{df['composite_score'].mean():.1f}")
    with col2:
        st.metric("Stocks Analyzed", len(results))
    with col3:
        st.metric("Buy Rated", len(df[df['rating'] == 'Buy']))
    
    # Detailed results
    st.subheader("Analysis Results")
    for result in sorted(results, key=lambda x: x['composite_score'], reverse=True):
        with st.expander(f"{result['name']} ({result['ticker']}) - {result['rating']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("Scores:")
                for name, score in result['component_scores'].items():
                    st.write(f"{name}: {score:.1f}")
            with col2:
                st.write("Key Metrics:")
                for name, value in result['key_metrics'].items():
                    if isinstance(value, float):
                        st.write(f"{name}: {value:.1f}")
                    else:
                        st.write(f"{name}: {value}")
    pass

if __name__ == "__main__":
    main()