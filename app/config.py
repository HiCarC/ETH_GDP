import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
    OPENSEA_API_KEY = os.getenv('OPENSEA_API_KEY')
    
    # Cache config
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Other configs
    ETHEREUM_ADDRESS = "0x0000000000000000000000000000000000000000"
    UPDATE_INTERVAL = 300  # 5 minutes 
    ENABLE_TIMELINE = False  # Feature flag for timeline