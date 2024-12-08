import requests
from app import cache
from datetime import datetime, timedelta
import pandas as pd

class FeesService:
    @staticmethod
    @cache.memoize(timeout=300)
    def get_eth_protocol_revenue():
        try:
            # Using CryptoStats API for protocol fees
            today = datetime.now().strftime('%Y-%m-%d')
            url = f'https://api.cryptostats.community/api/v1/fees/oneDayTotalFees/{today}'
            
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"CryptoStats API returned status code {response.status_code}")
                
            data = response.json()
            
            # Find Ethereum's fees
            eth_fees = next(
                (item['value'] for item in data 
                 if item.get('metadata', {}).get('name', '').lower() == 'ethereum'),
                0
            )
            
            # Convert to annual fees
            annual_fees = float(eth_fees) * 365
            
            # Get yesterday's fees for 24h change calculation
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_url = f'https://api.cryptostats.community/api/v1/fees/oneDayTotalFees/{yesterday}'
            yesterday_response = requests.get(yesterday_url)
            
            if yesterday_response.status_code == 200:
                yesterday_data = yesterday_response.json()
                yesterday_fees = next(
                    (item['value'] for item in yesterday_data 
                     if item.get('metadata', {}).get('name', '').lower() == 'ethereum'),
                    0
                )
                
                # Calculate 24h change
                if yesterday_fees > 0:
                    change_24h = ((float(eth_fees) - float(yesterday_fees)) / float(yesterday_fees)) * 100
                else:
                    change_24h = 0
                    
                return {
                    'current': annual_fees,
                    'change_24h': change_24h
                }
            
            return {
                'current': annual_fees,
                'change_24h': 0
            }

        except Exception as e:
            print(f"Error fetching protocol revenue: {e}")
            
            # Fallback to DeFiLlama fees API
            try:
                response = requests.get("https://api.llama.fi/overview/fees/ethereum")
                if response.status_code == 200:
                    data = response.json()
                    daily_fees = float(data.get('total24h', 0))
                    yesterday_fees = float(data.get('total48to24', 0))
                    
                    # Calculate 24h change using DeFiLlama data
                    if yesterday_fees > 0:
                        change_24h = ((daily_fees - yesterday_fees) / yesterday_fees) * 100
                    else:
                        change_24h = 0
                        
                    return {
                        'current': daily_fees * 365,
                        'change_24h': change_24h
                    }
            except Exception as e:
                print(f"Error fetching backup fee data: {e}")
                
            return {'current': 0, 'change_24h': 0}

    @staticmethod
    @cache.memoize(timeout=3600)
    def get_historical_fees(start_date, end_date):
        try:
            response = requests.get(
                "https://api.llama.fi/summary/fees/ethereum"
            )
            if response.status_code != 200:
                raise Exception(f"DeFiLlama API returned status code {response.status_code}")
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['totalDataChart'])
            df.columns = ['date', 'fees']
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df.set_index('date', inplace=True)
            
            # Filter date range and annualize fees
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]['fees'] * 365
            
        except Exception as e:
            print(f"Error fetching historical fee data: {e}")
            return pd.Series() 