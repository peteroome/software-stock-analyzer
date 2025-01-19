# app.py
import streamlit as st
import pandas as pd
from src.analyzer import CompleteStockAnalyzer
from src.constants import load_universe

def display_results(results):
    if not results:
        st.warning("No results to display")
        return

    # Convert to DataFrame for easier display
    df = pd.DataFrame(results)
    
    # Summary metrics
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Score", f"{df['composite_score'].mean():.1f}")
    with col2:
        st.metric("Stocks Analyzed", len(results))
    with col3:
        st.metric("Buy Rated", len(df[df['rating'].isin(['Buy', 'Strong Buy'])])) # Include Strong Buy
    
    # Overall distribution
    st.subheader("Rating Distribution")
    rating_counts = df['rating'].value_counts()
    st.bar_chart(rating_counts)
    
    # Detailed results
    st.subheader("Detailed Analysis")
    for result in sorted(results, key=lambda x: x['composite_score'], reverse=True):
        with st.expander(f"{result['name']} ({result['ticker']}) - {result['rating']} - Score: {result['composite_score']:.1f}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Component Scores:")
                for name, score in result['component_scores'].items():
                    # Format name for better display
                    formatted_name = name.replace('_', ' ').title()
                    st.write(f"{formatted_name}: {score:.1f}")
            
            with col2:
                st.write("Key Metrics:")
                for name, value in result['key_metrics'].items():
                    # Format name for better display
                    formatted_name = name.replace('_', ' ').title()
                    if isinstance(value, float):
                        st.write(f"{formatted_name}: {value:.1f}")
                    else:
                        st.write(f"{formatted_name}: {value}")

# Add debugging information
def main():
    st.title("Software Stock Analyzer")
    
    # Load universe
    universe = load_universe()
    
    if universe.empty:
        st.error("No universe file found. Please run the universe builder first.")
        return
    
    # Debug info
    st.sidebar.header("Analysis Controls")
    st.sidebar.subheader("Universe Statistics")
    st.sidebar.write(f"Total Stocks: {len(universe)}")
    st.sidebar.write(f"Available Columns: {', '.join(universe.columns)}")

    col1, col2 = st.sidebar.columns([3,1])
    with col1:
        st.write("Stock Selection")
    with col2:
        select_all = st.checkbox("Select All", value=True)
    
    # Stock selection
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks to Analyze",
        universe['ticker'].tolist(),
        default=universe['ticker'].unique().tolist() if select_all else []
    )
    
    # Run analysis button
    if st.sidebar.button("Run Analysis"):
        if not selected_stocks:
            st.warning("Please select at least one stock to analyze")
            return
            
        analyzer = CompleteStockAnalyzer()
        results = []
        
        # Progress bar
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(selected_stocks):
            progress_text.text(f"Analyzing {ticker} ({i+1}/{len(selected_stocks)})")
            result = analyzer.analyze_stock(ticker)
            if result and 'composite_score' in result:
                results.append(result)
            progress_bar.progress((i + 1) / len(selected_stocks))
        
        progress_text.text("Analysis complete!")
        
        # Display results
        if results:
            display_results(results)
        else:
            st.error("No valid results found. Please try different stocks.")

if __name__ == "__main__":
    main()