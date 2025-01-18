import yfinance as yf
import pandas as pd
from typing import List, Dict, Tuple
import time
from datetime import datetime

class UniverseBuilder:
    def __init__(self):
        self.min_market_cap = 1_000_000_000  # $1B
        self.max_market_cap = 70_000_000_000  # $70B
        self.min_volume = 100_000
        
        # Software/Tech related keywords for filtering
        self.relevant_industries = [
            'Software', 'Technology', 'Cloud Computing', 'Internet Services',
            'Information Technology', 'Software—Application', 'Software—Infrastructure',
            'Computer Hardware', 'Semiconductors', 'Information Technology Services'
        ]
        
        # Known software/tech companies to ensure we don't miss them
        self.known_tickers = [
            # Software/Cloud/SaaS
            'DDOG', 'NET', 'CFLT', 'MDB', 'SNOW', 'PLTR', 'CRWD', 'ZS', 'PANW',
            'DOCN', 'S', 'AI', 'PATH', 'U', 'GTLB', 'HCAT', 'API', 'DT',
            'BILL', 'NCNO', 'FRSH', 'APP', 'SUMO', 'ESTC', 'MGNI', 'TTD',
            'TWLO', 'DOMO', 'PD', 'FROG', 'APPN', 'COUP', 'AVLR', 'NTNX',
            'TEAM', 'OKTA', 'DOCU', 'SMAR', 'DBX', 'BOX', 'NOW', 'WDAY',
            'ZI', 'DAVA', 'NABL', 'BL', 'PAYC', 'PCTY', 'RNG', 'NICE',

            # Infrastructure/Hardware/Semiconductors
            'SMCI', 'NVDA', 'AMD', 'AMAT', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
            'WOLF', 'POWI', 'MPWR', 'LSCC', 'DIOD', 'SLAB', 'MRVL', 'SWKS',
            'ENTG', 'CCMP', 'ONTO', 'TER', 'ACLS', 'MTSI', 'ADI', 'NXPI',

            # Cybersecurity
            'CRWD', 'ZS', 'PANW', 'FTNT', 'CYBR', 'RPD', 'S', 'TENB',
            'SCWX', 'VRNS', 'SAIL', 'OCFT', 'SSTI', 'KNBE', 'RDWR',

            # Fintech
            'COIN', 'HOOD', 'UPST', 'AFRM', 'SOFI', 'MQ', 'PAYO', 'FLYW',
            'TOST', 'DLO', 'AVDX', 'PSFE', 'RELY',

            # AI/ML/Data
            'AI', 'PLTR', 'SNOW', 'TDC', 'VRNS', 'SPSC', 'NEWR',
            'BAND', 'SPLK', 'PLAN', 'DOMO', 'ALTR', 'BIGB',

            # Dev Tools/Infrastructure
            'GTLB', 'TWLO', 'FSLY', 'CFLT', 'DDOG', 'NET', 'API', 'PATH',
            'FORG', 'ESTC', 'NEWR', 'APPN', 'PD', 'FROG',

            # Enterprise Software
            'WDAY', 'NOW', 'TEAM', 'COUP', 'BILL', 'PCTY', 'PAYC', 'CSGS',
            'MANH', 'AZPN', 'PEGA', 'PRGS', 'BL', 'ADBE', 'CRM', 'INTU',

            # Emerging Tech
            'IONQ', 'RGTI', 'ARQQ', 'KVUE', 'DNA', 'HLLY', 'ACHR', 'GROY',
            'ALIT', 'OUST', 'MAPS', 'MKFG'
        ]
        
        self.invalid_tickers = set()  # Track invalid tickers

    def verify_ticker(self, ticker: str) -> bool:
        """Verify if a ticker is valid"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return 'regularMarketPrice' in info or 'currentPrice' in info
        except:
            return False

    def filter_stock(self, ticker: str) -> Dict:
        """Apply filters to determine if stock meets criteria"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Basic info check
            if not info or 'marketCap' not in info:
                self.invalid_tickers.add(ticker)
                return None
                
            market_cap = info.get('marketCap', 0)
            avg_volume = info.get('averageVolume', 0)
            industry = info.get('industry', '')
            sector = info.get('sector', '')
            
            # Check basic criteria
            if (self.min_market_cap <= market_cap <= self.max_market_cap and
                avg_volume >= self.min_volume):
                
                # Check if it's software/tech related
                is_tech = (
                    any(ind in str(industry) for ind in self.relevant_industries) or
                    any(ind in str(sector) for ind in self.relevant_industries) or
                    'Technology' in str(sector) or
                    ticker in self.known_tickers  # Include known tickers regardless
                )
                
                if is_tech:
                    return {
                        'ticker': ticker,
                        'name': info.get('longName', ticker),
                        'market_cap': market_cap / 1e9,
                        'industry': industry,
                        'sector': sector,
                        'avg_volume': avg_volume,
                        'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                        'gross_margins': info.get('grossMargins', 0) * 100 if info.get('grossMargins') else None,
                        'ps_ratio': info.get('priceToSalesTrailing12Months', None),
                        'is_known_ticker': ticker in self.known_tickers,
                        'price': info.get('currentPrice', info.get('regularMarketPrice', None))
                    }
            
            return None
            
        except Exception as e:
            self.invalid_tickers.add(ticker)
            print(f"Error filtering {ticker}: {str(e)}")
            return None

    def build_universe(self) -> Tuple[pd.DataFrame, List[str]]:
        """Build universe using known tickers first"""
        print("Processing known tickers first...")
        qualified_stocks = []
        
        # Process known tickers first
        for i, ticker in enumerate(self.known_tickers):
            if i % 10 == 0:  # Progress update
                print(f"Processing known ticker {i+1}/{len(self.known_tickers)}")
            
            result = self.filter_stock(ticker)
            if result:
                qualified_stocks.append(result)
            time.sleep(0.1)  # Rate limiting
        
        # Create DataFrame
        df = pd.DataFrame(qualified_stocks)
        
        if not df.empty:
            # Sort by market cap
            df = df.sort_values('market_cap', ascending=False)
            
            # Add growth categorization
            df['growth_category'] = pd.cut(
                df['revenue_growth'],
                bins=[-float('inf'), 0, 20, 40, float('inf')],
                labels=['Negative', 'Low', 'Medium', 'High']
            )
        
        return df, list(self.invalid_tickers)

    def save_universe(self, df: pd.DataFrame):
        """Save universe to CSV with timestamp"""
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f'software_universe_{date_str}.csv'
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} stocks to {filename}")
        
        # Save invalid tickers
        if self.invalid_tickers:
            with open(f'invalid_tickers_{date_str}.txt', 'w') as f:
                f.write('\n'.join(sorted(self.invalid_tickers)))
            print(f"Saved {len(self.invalid_tickers)} invalid tickers to invalid_tickers_{date_str}.txt")

def main():
    builder = UniverseBuilder()
    print("Building software stock universe...")
    
    universe, invalid_tickers = builder.build_universe()
    
    print("\nUniverse Summary:")
    print(f"Total valid stocks: {len(universe)}")
    print(f"Invalid tickers: {len(invalid_tickers)}")
    
    if not universe.empty:
        print("\nBreakdown by Growth Category:")
        print(universe['growth_category'].value_counts())
        
        print("\nBreakdown by Market Cap ($B):")
        market_cap_bins = [1, 5, 10, 20, 50, 70]
        universe['market_cap_category'] = pd.cut(
            universe['market_cap'],
            bins=[0] + market_cap_bins,
            labels=[f'${b}B' for b in market_cap_bins]
        )
        print(universe['market_cap_category'].value_counts())
        
        print("\nTop 20 by market cap:")
        display_cols = ['ticker', 'name', 'market_cap', 'price', 'industry', 'revenue_growth', 'ps_ratio']
        print(universe[display_cols].head(20).to_string())
    
    # Save results
    builder.save_universe(universe)
    
    if invalid_tickers:
        print("\nInvalid tickers found:")
        print(', '.join(sorted(invalid_tickers)))

if __name__ == "__main__":
    main()