import requests
from app import cache
import pandas as pd

class DefiLlamaService:
    BASE_URL = "https://api.llama.fi"
    
    @staticmethod
    @cache.memoize(timeout=300)
    def get_eth_tvl():
        try:
            # Get current TVL with stablecoins excluded
            response = requests.get(
                f"{DefiLlamaService.BASE_URL}/v2/historicalChainTvl/ethereum", 
                params={
                    "excludeStablecoins": "true",
                    "includePrices": "true"
                }
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            if not data:
                return 0
                
            # Get latest TVL point and 24h ago point
            latest_tvl = float(data[-1]['tvl'])
            
            # Find TVL from 24h ago
            current_timestamp = data[-1]['date']
            target_timestamp = current_timestamp - (24 * 3600)  # 24 hours ago
            
            # Find the closest point to 24h ago
            for point in reversed(data[:-1]):  # Exclude latest point
                if point['date'] <= target_timestamp:
                    tvl_24h_ago = float(point['tvl'])
                    # Calculate percentage change
                    change_24h = ((latest_tvl - tvl_24h_ago) / tvl_24h_ago) * 100
                    return {
                        'current': latest_tvl,
                        'change_24h': change_24h
                    }
            
            return {
                'current': latest_tvl,
                'change_24h': 0
            }
            
        except Exception as e:
            print(f"Error fetching ETH TVL: {e}")
            return {'current': 0, 'change_24h': 0}
            
    @staticmethod
    @cache.memoize(timeout=300)
    def get_stablecoin_supply():
        try:
            # Get stablecoins data
            response = requests.get(
                "https://stablecoins.llama.fi/stablecoins?includePrices=true"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama Stablecoins API returned status code {response.status_code}")
            
            data = response.json()
            
            # List of major Ethereum stablecoins to track
            eth_stablecoins = ['USDT', 'USDC', 'DAI', 'FRAX', 'LUSD', 'USDD']
            
            eth_stables = sum(
                float(asset['chainCirculating'].get('Ethereum', {}).get('current', {}).get('peggedUSD', 0))
                for asset in data['peggedAssets']
                if asset['symbol'] in eth_stablecoins
            )
            
            return eth_stables
        except Exception as e:
            print(f"Error fetching stablecoin supply: {e}")
            return 0 

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_tvl(start_date, end_date):
        try:
            response = requests.get(
                f"{DefiLlamaService.BASE_URL}/v2/historicalChainTvl/ethereum"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df.set_index('date', inplace=True)
            
            # Filter date range and resample
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]['tvl']
            
        except Exception as e:
            print(f"Error fetching historical TVL: {e}")
            return pd.Series()

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_stables(start_date, end_date):
        try:
            response = requests.get(
                "https://stablecoins.llama.fi/stablecoincharts/Ethereum"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df.set_index('date', inplace=True)
            
            # Filter date range
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]['totalCirculating']
            
        except Exception as e:
            print(f"Error fetching historical stablecoin data: {e}")
            return pd.Series()