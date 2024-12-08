import requests
from app.config import Config
from app import cache
import pandas as pd

class CoinGeckoService:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    @staticmethod
    @cache.memoize(timeout=300)
    def get_eth_market_data():
        try:
            response = requests.get(
                f"{CoinGeckoService.BASE_URL}/simple/price",
                params={
                    "ids": "ethereum",
                    "vs_currencies": "usd",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true"
                }
            )
            if response.status_code != 200:
                raise Exception(f"CoinGecko API returned status code {response.status_code}")
                
            data = response.json()['ethereum']
            return {
                'market_cap': data['usd_market_cap'],
                'price_change_24h': data['usd_24h_change'],
                'volume_24h': data['usd_24h_vol'],
                'current_price': data['usd']
            }
        except Exception as e:
            print(f"Error fetching ETH market data: {e}")
            return {
                'market_cap': 0,
                'price_change_24h': 0,
                'volume_24h': 0,
                'current_price': 0
            }

    @staticmethod
    @cache.memoize(timeout=300)
    def get_protocol_market_caps():
        # Top Ethereum DeFi protocols
        protocols = {
            'uniswap': 'uniswap',
            'aave': 'aave',
            'chainlink': 'chainlink',
            'maker': 'maker',
            'compound': 'compound-governance-token',
            'curve-dao-token': 'curve-dao-token',
            'synthetix': 'synthetix-network-token',
            'lido-dao': 'lido-dao',
            'arbitrum': 'arbitrum',
            'optimism': 'optimism'
        }
        
        try:
            # Batch request all protocols at once
            ids = ','.join(protocols.values())
            response = requests.get(
                f"{CoinGeckoService.BASE_URL}/simple/price",
                params={
                    "ids": ids,
                    "vs_currencies": "usd",
                    "include_market_cap": "true"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"CoinGecko API returned status code {response.status_code}")
                
            data = response.json()
            total_mcap = sum(
                data[protocol_id]['usd_market_cap']
                for protocol_id in protocols.values()
                if protocol_id in data and 'usd_market_cap' in data[protocol_id]
            )
            
            return total_mcap
        except Exception as e:
            print(f"Error fetching protocol market caps: {e}")
            return 0 

    @staticmethod
    @cache.memoize(timeout=3600)  # Cache for 1 hour
    def get_historical_market_data(start_date, end_date, interval):
        try:
            response = requests.get(
                f"{CoinGeckoService.BASE_URL}/coins/ethereum/market_chart/range",
                params={
                    "vs_currency": "usd",
                    "from": int(start_date.timestamp()),
                    "to": int(end_date.timestamp())
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"CoinGecko API returned status code {response.status_code}")
                
            data = response.json()
            # Convert to DataFrame and resample to desired interval
            df = pd.DataFrame(data['market_caps'], columns=['timestamp', 'value'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df.resample(interval).last()['value']
            
        except Exception as e:
            print(f"Error fetching historical market data: {e}")
            return pd.Series()

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_protocol_mcaps(start_date, end_date):
        protocols = {
            'uniswap': 'uniswap',
            'aave': 'aave',
            'chainlink': 'chainlink',
            'maker': 'maker',
            'compound': 'compound-governance-token',
            'curve-dao-token': 'curve-dao-token',
            'synthetix': 'synthetix-network-token',
            'lido-dao': 'lido-dao'
        }
        
        try:
            all_data = pd.DataFrame()
            
            for protocol_id in protocols.values():
                response = requests.get(
                    f"{CoinGeckoService.BASE_URL}/coins/{protocol_id}/market_chart/range",
                    params={
                        "vs_currency": "usd",
                        "from": int(start_date.timestamp()),
                        "to": int(end_date.timestamp())
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data['market_caps'], columns=['timestamp', protocol_id])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    
                    if all_data.empty:
                        all_data = df
                    else:
                        all_data = all_data.join(df, how='outer')
            
            return all_data.sum(axis=1)
            
        except Exception as e:
            print(f"Error fetching historical protocol market caps: {e}")
            return pd.Series()

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_market_cap(coin_id, start_date, end_date, interval):
        try:
            response = requests.get(
                f"{CoinGeckoService.BASE_URL}/coins/{coin_id}/market_chart/range",
                params={
                    "vs_currency": "usd",
                    "from": int(start_date.timestamp()),
                    "to": int(end_date.timestamp())
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"CoinGecko API returned status code {response.status_code}")
            
            data = response.json()
            df = pd.DataFrame(data['market_caps'], columns=['timestamp', 'value'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df['value'].resample(interval).last()
            
        except Exception as e:
            logger.error(f"Error fetching historical market cap: {e}")
            return pd.Series()

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_defi_mcap(start_date, end_date, interval):
        protocols = [
            'uniswap', 'aave', 'chainlink', 'maker',
            'compound-governance-token', 'curve-dao-token',
            'synthetix-network-token', 'lido-dao'
        ]
        
        try:
            all_data = pd.DataFrame()
            
            for protocol in protocols:
                response = requests.get(
                    f"{CoinGeckoService.BASE_URL}/coins/{protocol}/market_chart/range",
                    params={
                        "vs_currency": "usd",
                        "from": int(start_date.timestamp()),
                        "to": int(end_date.timestamp())
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data['market_caps'], columns=['timestamp', 'value'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    
                    if all_data.empty:
                        all_data = df
                    else:
                        all_data = all_data.add(df, fill_value=0)
            
            return all_data['value'].resample(interval).last()
            
        except Exception as e:
            logger.error(f"Error fetching historical DeFi market caps: {e}")
            return pd.Series()