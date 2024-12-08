from flask import Blueprint, jsonify, render_template
from app.services.coingecko import CoinGeckoService
from app.services.defillama import DefiLlamaService
from app.services.fees import FeesService
from app.services.nft import NFTService
from app import cache
import logging
from datetime import datetime, timedelta
import pandas as pd
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/gdp')
@cache.cached(timeout=60)
def get_gdp():
    try:
        # Get all component data with proper error handling
        eth_market_data = CoinGeckoService.get_eth_market_data()
        if not eth_market_data['market_cap']:
            raise Exception("Failed to fetch ETH market data")
        logger.info("Successfully fetched ETH market data")
        
        # Monetary Base (M)
        M = eth_market_data['market_cap']
        
        # TVL (K)
        tvl_data = DefiLlamaService.get_eth_tvl()
        K = tvl_data['current']
        if not K:
            logger.warning("TVL data returned 0")
        logger.info("Successfully fetched TVL data")
        tvl_change = tvl_data['change_24h']
        
        # Fees (F)
        fees_data = FeesService.get_eth_protocol_revenue()
        F = fees_data['current']
        if not F:
            logger.warning("Protocol revenue data returned 0")
        logger.info("Successfully fetched protocol revenue data")
        fees_change = fees_data['change_24h']
        
        # Stablecoins and Bridged Assets (S)
        S = DefiLlamaService.get_stablecoin_supply()
        if not S:
            logger.warning("Stablecoin data returned 0")
        logger.info("Successfully fetched stablecoin data")
        
        # Protocol Market Caps (P)
        P = CoinGeckoService.get_protocol_market_caps()
        if not P:
            logger.warning("Protocol market caps returned 0")
        logger.info("Successfully fetched protocol market caps")
        
        gdp = M + K + F + S + P
        
        return jsonify({
            'gdp': gdp,
            'components': {
                'monetary_base': M,
                'tvl': K,
                'fees': F,
                'stablecoins': S,
                'protocols': P
            },
            'metadata': {
                'eth_price': eth_market_data['current_price'],
                'eth_24h_change': eth_market_data['price_change_24h'],
                'eth_24h_volume': eth_market_data['volume_24h'],
                'tvl_24h_change': tvl_change,
                'fees_24h_change': fees_change
            }
        })
    except Exception as e:
        logger.error(f"Error calculating GDP: {str(e)}")
        return jsonify({'error': 'Failed to calculate GDP'}), 500

@main.route('/methodology')
def methodology():
    components = [
        {
            'title': 'Monetary Base (M)',
            'symbol': 'M',
            'description': 'Market capitalization of ETH, representing the fundamental monetary layer.',
            'calculation': 'ETH Price × Circulating Supply',
            'source': 'CoinGecko API',
            'rationale': 'Reflects the network\'s capacity to serve as a monetary jurisdiction'
        },
        {
            'title': 'DeFi Capital Stock (K)',
            'symbol': 'K',
            'description': 'Total Value Locked across DeFi protocols, analogous to productive capital in traditional economies.',
            'calculation': 'Sum of all assets locked in Ethereum DeFi protocols',
            'source': 'DeFiLlama API',
            'rationale': 'Measures capital actively deployed in the ecosystem'
        },
        {
            'title': 'Fee Revenue (F)',
            'symbol': 'F',
            'description': 'Annualized fees generated at both L1 and protocol levels.',
            'calculation': '(Daily L1 Fees + Protocol Fees) × 365',
            'source': 'DeFiLlama Fees API',
            'rationale': 'Indicates willingness to pay for blockspace and services'
        },
        {
            'title': 'Stablecoins (S)',
            'symbol': 'S',
            'description': 'External capital integrated into the Ethereum ecosystem.',
            'calculation': 'Total Stablecoin Supply + Wrapped Asset Value',
            'source': 'DeFiLlama Stablecoins API',
            'rationale': 'Measures external capital attraction and integration'
        },
        {
            'title': 'Protocol Market Caps (P)',
            'symbol': 'P',
            'description': 'Aggregate value of native protocols and applications.',
            'calculation': 'Sum of Protocol Token Market Caps',
            'source': 'CoinGecko API',
            'rationale': 'Represents the ecosystem\'s "industrial base"'
        },
        {
            'title': 'Cultural Capital (C)',
            'symbol': 'C',
            'description': 'Value of NFTs and cultural assets in the ecosystem.',
            'calculation': 'Sum of (Floor Price × Collection Size) for major NFTs',
            'source': 'DeFiLlama NFTs API',
            'rationale': 'Captures cultural and creative value'
        }
    ]

    metrics = {
        'current_gdp': {
            'value': '$709.39B',
            'comparison': 'Comparable to Switzerland\'s GDP'
        },
        'growth_rate': {
            'value': '127%',
            'period': 'Year over Year'
        },
        'total_txs': {
            'value': '1.8B+',
            'description': 'Total Transactions'
        }
    }

    projections = {
        'current': {
            'year': '2024',
            'value': '$709.39B',
            'comparison': 'Current State'
        },
        'short_term': {
            'year': '2025',
            'value': '$1.2T',
            'growth': '69%'
        },
        'medium_term': {
            'year': '2030',
            'value': '$5.4T',
            'cagr': '45%'
        },
        'long_term': {
            'year': '2035',
            'value': '$18T',
            'description': 'Full Adoption Scenario'
        }
    }

    return render_template('methodology.html', 
                         components=components,
                         metrics=metrics,
                         projections=projections)

@main.route('/api/gdp/historical/<period>')
@cache.cached(timeout=300)
def get_historical_gdp(period):
    try:
        end_date = datetime.now()
        
        # Define timeframes
        if period == '24h':
            start_date = end_date - timedelta(days=1)
            interval = '1h'
        elif period == '1w':
            start_date = end_date - timedelta(weeks=1)
            interval = '4h'
        elif period == '1m':
            start_date = end_date - timedelta(days=30)
            interval = '1d'
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
            interval = '1d'
        else:
            return jsonify({'error': 'Invalid period'}), 400

        # Get historical data from each service
        eth_data = CoinGeckoService.get_historical_market_data(start_date, end_date, interval)
        tvl_data = DefiLlamaService.get_historical_tvl(start_date, end_date)
        fees_data = FeesService.get_historical_fees(start_date, end_date)
        stables_data = DefiLlamaService.get_historical_stables(start_date, end_date)
        protocols_data = CoinGeckoService.get_historical_protocol_mcaps(start_date, end_date)
        nft_data = NFTService.get_historical_nft_data(start_date, end_date)

        # Combine all data into a pandas DataFrame for easy manipulation
        df = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date, freq=interval))
        
        df['monetary_base'] = eth_data
        df['tvl'] = tvl_data
        df['fees'] = fees_data
        df['stablecoins'] = stables_data
        df['protocols'] = protocols_data
        df['cultural'] = nft_data
        
        # Calculate total GDP for each timestamp
        df['gdp'] = df.sum(axis=1)
        
        # Format dates for chart labels
        if period == '24h':
            labels = [d.strftime('%H:%M') for d in df.index]
        elif period == '1w':
            labels = [d.strftime('%a %H:%M') for d in df.index]
        elif period in ['1m', '1y']:
            labels = [d.strftime('%Y-%m-%d') for d in df.index]

        return jsonify({
            'labels': labels,
            'values': df['gdp'].tolist(),
            'components': {
                'monetary_base': df['monetary_base'].tolist(),
                'tvl': df['tvl'].tolist(),
                'fees': df['fees'].tolist(),
                'stablecoins': df['stablecoins'].tolist(),
                'protocols': df['protocols'].tolist(),
                'cultural': df['cultural'].tolist()
            }
        })

    except Exception as e:
        logger.error(f"Error fetching historical GDP data: {str(e)}")
        return jsonify({'error': 'Failed to fetch historical data'}), 500 