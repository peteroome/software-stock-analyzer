# app.py
import streamlit as st
import pandas as pd
from src.analyzer import CompleteStockAnalyzer
from src.constants import load_universe

st.set_page_config(layout="wide") 

def display_results(results):
    if not results:
        st.warning("No results to display")
        return

    df = pd.DataFrame(results)
    
    # Create overview dataframe
    overview_df = pd.DataFrame({
        'Ticker': df['ticker'],
        'Name': df['name'],
        'Score': df['composite_score'].round(1),
        'Rating': df['rating'],
        'Market Cap ($B)': df['market_cap'].round(1),
        'Growth (%)': df.apply(lambda x: x['key_metrics'].get('revenue_growth', 'N/A'), axis=1).round(1),
        'Momentum': df.apply(lambda x: get_momentum_indicator(x['key_metrics']), axis=1),
        'Price Trend': df.apply(lambda x: get_price_trend(x['key_metrics']), axis=1),
    })

    # Detail View first (at the top)
    detail_section = st.container()
    
    # Table View below
    table_section = st.container()

    # Table View with selection
    with table_section:
        st.subheader("All Results")

        # Display the table
        st.dataframe(
            overview_df,
            use_container_width=True,
            height=int(len(results) * 35.5),
            hide_index=True,
            column_config={
                "Ticker": st.column_config.TextColumn(
                    "Ticker",
                    width="small",
                ),
                "Name": st.column_config.TextColumn(
                    "Name",
                    width="medium",
                ),
                "Score": st.column_config.NumberColumn(
                    "Score",
                    width="small",
                    format="%.1f"
                ),
                "Rating": st.column_config.TextColumn(
                    "Rating",
                    width="small",
                ),
                "Market Cap ($B)": st.column_config.NumberColumn(
                    "Market Cap ($B)",
                    width="small",
                    format="%.1f"
                ),
                "Growth (%)": st.column_config.NumberColumn(
                    "Growth (%)",
                    width="small",
                    format="%.1f"
                ),
                "Momentum": st.column_config.TextColumn(
                    "Momentum",
                    width="small",
                ),
                "Price Trend": st.column_config.TextColumn(
                    "Price Trend",
                    width="medium",
                ),
            }
        )
    
    # Detail View
    with detail_section:
        # Add selection dropdown
        selected_row = st.selectbox(
            "Select a stock to view details",
            overview_df['Ticker'].tolist(),
            format_func=lambda x: f"{x} - {overview_df[overview_df['Ticker'] == x]['Name'].iloc[0]}"
        )
        st.session_state.selected_ticker = selected_row

        st.header("Focused View")

        if 'selected_ticker' in st.session_state:
            result = next(r for r in results if r['ticker'] == st.session_state.selected_ticker)
            
            # Create three columns for key metrics
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.metric("Ticker", f"{result['name']} ({result['ticker']})")
            with col2:
                st.metric("Rating", result['rating'])
            with col3:
                st.metric("Score", f"{result['composite_score']:.1f}")
            with col4:
                st.metric("Market Cap", f"${result['market_cap']:.1f}B")
            
            # Create two columns for detailed analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Analysis Scores")
                scores_df = pd.DataFrame({
                    'Component': [
                        'Composite Score',
                        'Growth',
                        'Value Alignment',
                        'Margins',
                        'Financial Health',
                        'Insider Confidence',
                        'Momentum',
                        'Volume Trends'
                    ],
                    'Score': [
                        result['composite_score'],
                        result['component_scores']['growth'],
                        result['component_scores']['value_alignment'],
                        result['component_scores']['margins'],
                        result['component_scores']['financial_health'],
                        result['component_scores']['insider_confidence'],
                        result['component_scores']['momentum'],
                        result['component_scores']['volume_trends']
                    ]
                })
                st.dataframe(
                    scores_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Score": st.column_config.NumberColumn(
                            "Score",
                            format="%.1f"
                        )
                    }
                )
            
            with col2:
                st.subheader("Fundamental Metrics")
                metrics = result['key_metrics']
                fundamentals_df = pd.DataFrame({
                    'Metric': [
                        'P/S Ratio',
                        'Revenue Growth (%)',
                        'Gross Margins (%)',
                        'Current Ratio',
                        'Cash/Debt Ratio',
                        'Insider Ownership (%)',
                        'Institutional Ownership (%)',
                        'Price vs 50-day MA (%)',
                        'Price vs 200-day MA (%)'
                    ],
                    'Value': [
                        metrics['ps_ratio'],
                        metrics['revenue_growth'],
                        metrics['gross_margins'],
                        metrics['current_ratio'],
                        metrics['cash_to_debt'],
                        metrics['insider_ownership'],
                        metrics['institutional_ownership'],
                        metrics['price_vs_ma50'],
                        metrics['price_vs_ma200']
                    ]
                })
                st.dataframe(
                    fundamentals_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Value": st.column_config.NumberColumn(
                            "Value",
                            format="%.1f"
                        )
                    }
                )

def get_momentum_indicator(metrics):
    """
    Determine momentum based on price vs moving averages
    Returns: 🔥 (Strong), ↗️ (Up), ➡️ (Neutral), ↘️ (Down), ❄️ (Weak)
    """
    price_vs_50 = metrics.get('price_vs_ma50', 0)
    price_vs_200 = metrics.get('price_vs_ma200', 0)
    
    if price_vs_50 > 5 and price_vs_200 > 10:
        return "🔥 Strong"
    elif price_vs_50 > 0 and price_vs_200 > 0:
        return "↗️ Up"
    elif price_vs_50 < -5 and price_vs_200 < -10:
        return "❄️ Weak"
    elif price_vs_50 < 0 and price_vs_200 < 0:
        return "↘️ Down"
    else:
        return "➡️ Neutral"

def get_price_trend(metrics):
    """
    Compare short-term vs long-term trend
    Returns a string indicating trend direction and strength
    """
    ma50 = metrics.get('price_vs_ma50', 0)
    ma200 = metrics.get('price_vs_ma200', 0)
    volume_trend = metrics.get('volume_trend', 1)
    
    trend_strength = ""
    
    # Basic trend
    if ma50 > 2 and ma200 > 2:
        if volume_trend > 1.1:  # Increasing volume
            trend_strength = "📈 Strong Uptrend"
        else:
            trend_strength = "↗️ Uptrend"
    elif ma50 < -2 and ma200 < -2:
        if volume_trend < 0.9:  # Decreasing volume
            trend_strength = "📉 Strong Downtrend"
        else:
            trend_strength = "↘️ Downtrend"
    elif abs(ma50) <= 2 and abs(ma200) <= 2:
        trend_strength = "↔️ Sideways"
    elif ma50 > ma200:
        trend_strength = "↗️ Emerging Uptrend"
    else:
        trend_strength = "↘️ Emerging Downtrend"
    
    return trend_strength

def main():
    st.title("Software Stock Analyzer")

    # Add refresh button in the top right
    if st.button("🔄 Refresh Analysis"):
        # Clear the cached results
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        st.experimental_rerun()
    
    # Load universe
    universe = load_universe()
    
    if universe.empty:
        st.error("No universe file found. Please run the universe builder first.")
        return

    # Only run analysis if results are not in session state
    if 'analysis_results' not in st.session_state:
        analyzer = CompleteStockAnalyzer()
        results = []
        
        # Progress bar
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(universe['ticker']):
            progress_text.text(f"Analyzing {ticker} ({i+1}/{len(universe)})")
            result = analyzer.analyze_stock(ticker)
            if result and 'composite_score' in result:
                results.append(result)
            progress_bar.progress((i + 1) / len(universe))
        
        progress_text.text("Analysis complete!")
        
        # Store results in session state
        st.session_state.analysis_results = results

    # Display results using stored analysis
    if st.session_state.analysis_results:
        display_results(st.session_state.analysis_results)
    else:
        st.error("No valid results found. Check universe data.")

if __name__ == "__main__":
    main()