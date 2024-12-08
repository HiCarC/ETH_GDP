import requests
from app import cache
from datetime import datetime, timedelta
import pandas as pd

class NFTService:
    BASE_URL = "https://api.llama.fi"
    
    @staticmethod
    @cache.memoize(timeout=300)
    def get_total_nft_value():
        try:
            # Get NFT data from DeFiLlama
            response = requests.get(f"{NFTService.BASE_URL}/nfts/collections")
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
                
            data = response.json()
            
            # Filter for Ethereum collections and sum their market caps
            eth_collections = [
                collection for collection in data
                if 'Ethereum' in collection.get('chains', [])
            ]
            
            total_market_cap = sum(
                float(collection.get('marketCap', 0))
                for collection in eth_collections
            )
            
            # Get volume data
            volume_response = requests.get(f"{NFTService.BASE_URL}/nfts/volumes")
            if volume_response.status_code == 200:
                volume_data = volume_response.json()
                eth_volume = next(
                    (chain['volume1d'] for chain in volume_data 
                     if chain.get('name') == 'Ethereum'),
                    0
                )
                # Add annualized volume to market cap
                total_value = total_market_cap + (float(eth_volume) * 365)
            else:
                total_value = total_market_cap
            
            return total_value

        except Exception as e:
            print(f"Error fetching NFT data: {e}")
            return 0

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_nft_data(start_date, end_date):
        try:
            response = requests.get(
                f"{NFTService.BASE_URL}/nfts/historical/ethereum"
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
            return df.loc[mask]['totalMarketCap']
            
        except Exception as e:
            print(f"Error fetching historical NFT data: {e}")
            return pd.Series() 