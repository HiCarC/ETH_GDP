import requests
from app import cache
import pandas as pd

# Category mapping dictionary
CATEGORY_MAPPING = {
    "Liquid Staking": ("Staking Entities", "Restaking Asset issuer"),
    "Lending": ("Lending and Borrowing Provider", None),
    "Bridge": ("Service Providers", "Bridge"),
    "Dexes": ("Exchanges", "Decentralised Exchange (DEX)"),
    "Restaking": ("Staking Entities", "Restaking Asset issuer"),
    "Liquid Restaking": ("Staking Entities", "Restaking Asset issuer"),
    "CDP": ("Lending and Borrowing Provider", "Collateralised Debt Position (CDP) Issuer"),
    "Yield": ("Asset Managers", "Yield Farm"),
    "RWA": ("Asset Managers", "Real World Asset (RWA) Tokeniser"),
    "Farm": ("Asset Managers", "Yield Farm"),
    "Basis Trading": ("Miscellaneous", "Futures Issuer"),
    "Derivatives": ("Miscellaneous", "Synthetic Asset Issuer"),
    "Yield Aggregator": ("Asset Managers", "Yield Farm"),
    "Services": ("Service Providers", None),
    "Launchpad": ("Service Providers", "Launchpad"),
    "Cross Chain": ("Service Providers", "Bridge"),
    "Leveraged Farming": ("Asset Managers", "Yield Farm"),
    "Indexes": ("Asset Managers", "Indexer"),
    "Privacy": ("Service Providers", "Privacy / Security Provider"),
    "Staking Pool": ("Staking Entities", "Staking Pool"),
    "Synthetics": ("Miscellaneous", "Synthetic Asset Issuer"),
    "Payments": ("Service Providers", "Decentralised Payment Provider"),
    "Liquidity manager": ("Asset Managers", "Automated Portfolio Manager"),
    "Insurance": ("Miscellaneous", "Insurance Provider"),
    "Options": ("Miscellaneous", "Option Issuer"),
    "NFT Marketplace": ("Exchanges", "Decentralised Exchange (DEX)"),
    "NFT Lending": ("Lending and Borrowing Provider", "Traditional Collateralised Lenders"),
    "Decentralized Stablecoin": ("Decentralised Stablecoin Issuers", "Decentralised Fiat-Backed Stablecoin Issuer"),
    "Algo-Stables": ("Decentralised Stablecoin Issuers", "Decentralised Algorithmic Stablecoin Issuer"),
    "Prediction Market": ("Miscellaneous", "Futures Issuer"),
    "Options Vault": ("Miscellaneous", "Option Issuer"),
    "Uncollateralized Lending": ("Miscellaneous", "Others (Misc.)"),
    "RWA Lending": ("Lending and Borrowing Provider", "Traditional Collateralised Lenders"),
    "Reserve Currency": ("Miscellaneous", "Others (Misc.)"),
    "SoFi": ("Miscellaneous", "Others (Misc.)"),
    "DEX Aggregator": ("Exchanges", "DEX Aggregator"),
    "Gaming": ("Miscellaneous", "Others (Misc.)"),
    "NftFi": ("Miscellaneous", "Synthetic Asset Issuer"),
    "Ponzi": ("Miscellaneous", "Others (Misc.)"),
    "Oracle": ("Service Providers", "Oracle"),
    "Wallets": ("Miscellaneous", "Others (Misc.)"),
    "Telegram Bot": ("Miscellaneous", "Others (Misc.)"),
    "MEV": ("Miscellaneous", "Others (Misc.)"),
    "CEX": ("Exchanges", "Centralised Exchange (CEX)"),
    "Chain": ("Service Providers", "Bridge"),
}

def map_category(category: str) -> tuple[str, str]:
    """Map DeFiLlama category to CCAF category and subcategory."""
    ccaf_category, ccaf_sub_category = CATEGORY_MAPPING.get(
        category, ("Miscellaneous", "Others (Misc.)")
    )
    return ccaf_category, ccaf_sub_category or ccaf_category

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
            
            # Track individual amounts for distribution and get 24h change
            distribution = {
                'USDT': 0,
                'USDC': 0,
                'DAI': 0,
                'Others': 0
            }
            
            total_supply = 0
            total_supply_24h_ago = 0
            
            for asset in data['peggedAssets']:
                symbol = asset['symbol']
                if 'Ethereum' in asset.get('chainCirculating', {}):
                    current = asset['chainCirculating']['Ethereum'].get('current', {})
                    amount = float(current.get('peggedUSD', 0))
                    amount_24h = float(asset['chainCirculating']['Ethereum'].get('circulatingPrevDay', {}).get('peggedUSD', 0))
                    
                    total_supply += amount
                    total_supply_24h_ago += amount_24h
                    
                    if symbol in ['USDT', 'USDC', 'DAI']:
                        distribution[symbol] = amount
                    else:
                        distribution['Others'] += amount
            
            # Calculate 24h change percentage
            change_24h = ((total_supply - total_supply_24h_ago) / total_supply_24h_ago * 100) if total_supply_24h_ago > 0 else 0
            
            return {
                'total': total_supply,
                'change_24h': change_24h,
                'distribution': distribution
            }
        except Exception as e:
            print(f"Error fetching stablecoin supply: {e}")
            return {
                'total': 0,
                'change_24h': 0,
                'distribution': {
                    'USDT': 0,
                    'USDC': 0,
                    'DAI': 0,
                    'Others': 0
                }
            }

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
            
            # Extract USDT supply from totalCirculating.peggedUSD
            df['usdt_supply'] = df['totalCirculating'].apply(lambda x: x['peggedUSD'])
            
            # Filter date range
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]['usdt_supply']
            
        except Exception as e:
            print(f"Error fetching historical stablecoin data: {e}")
            return pd.Series()

    @staticmethod
    def get_usdt_supply():
        try:
            response = requests.get(
                "https://stablecoins.llama.fi/stablecoin/USDT?chain=Ethereum"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            return data['circulating']  # This will give you the current USDT supply on Ethereum
            
        except Exception as e:
            print(f"Error fetching USDT supply: {e}")
            return 0

    @staticmethod
    @cache.memoize(timeout=300)
    def get_top_protocols():
        try:
            response = requests.get(
                f"{DefiLlamaService.BASE_URL}/protocols"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            
            # Filter for Ethereum protocols and exclude CEX
            eth_protocols = [p for p in data if 'Ethereum' in p['chains'] and p.get('category', '').lower() != 'cex']
            eth_protocols.sort(key=lambda x: float(x.get('tvl', 0)), reverse=True)
            
            # Return top 10 protocols with relevant data
            return [{
                'name': p['name'],
                'tvl': float(p.get('tvl', 0)),
                'change_1d': float(p.get('change_1d', 0)),
                'category': map_category(p.get('category', 'Unknown'))[0]  # Use main category
            } for p in eth_protocols[:10]]
            
        except Exception as e:
            print(f"Error fetching top protocols: {e}")
            return []

    @staticmethod
    @cache.memoize(timeout=300)
    def get_category_distribution():
        try:
            response = requests.get(
                f"{DefiLlamaService.BASE_URL}/protocols"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            
            # Filter for Ethereum protocols and exclude CEX
            eth_protocols = [p for p in data if 'Ethereum' in p['chains'] and p.get('category', '').lower() != 'cex']
            
            # Calculate TVL by mapped category
            categories = {}
            for protocol in eth_protocols:
                original_category = protocol.get('category', 'Unknown')
                mapped_category = map_category(original_category)[0]  # Use main category
                tvl = float(protocol.get('tvl', 0))
                categories[mapped_category] = categories.get(mapped_category, 0) + tvl
            
            return categories
            
        except Exception as e:
            print(f"Error fetching category distribution: {e}")
            return {}

    @staticmethod
    @cache.memoize(timeout=300)
    def get_top_yields():
        try:
            response = requests.get(
                "https://yields.llama.fi/pools"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            
            # Filter for Ethereum pools and sort by APY
            eth_pools = [p for p in data['data'] if p['chain'] == 'Ethereum']
            eth_pools.sort(key=lambda x: float(x.get('apy', 0)), reverse=True)
            
            # Return top 10 yield opportunities
            return [{
                'pool': p['symbol'],
                'protocol': p['project'],
                'apy': float(p.get('apy', 0)),
                'tvl': float(p.get('tvlUsd', 0))
            } for p in eth_pools[:10]]
            
        except Exception as e:
            print(f"Error fetching yield data: {e}")
            return []