# Ethereum GDP Monitor 📊

## Purpose

With project I want to introduce a novel approach to valuing blockchain networks, specifically Ethereum, by treating them as emerging digital economies rather than traditional corporations. Indeed, traditional valuation methods often mischaracterize blockchain networks by applying corporate metrics to what are essentially sovereign, digital economies with their own reserve currencies.

### Why a New Valuation Framework?

Blockchain networks, particularly smart contract platforms like Ethereum, represent a paradigm shift in how we should think about digital economic systems:

- They are not merely businesses, but emerging network states
- They have their own monetary jurisdictions and reserve currencies
- They incorporate mechanisms analogous to government bonds (staking)
- They foster cultural and social value through NFTs and community
- They enable programmable economic activity through smart contracts

## The GDP Framework

The Gross Decentralized Product (GDP) framework captures six key components:

1. 💰 **Monetary Base ($M)**
   - ETH's market capitalization
   - Represents the fundamental monetary layer
   - Includes M1/M2 metrics

2. 🏦 **DeFi TVL ($K)**
   - Total Value Locked in DeFi protocols
   - Measures capital utilization
   - Indicates ecosystem trust and stability

3. 💸 **Protocol Revenue ($F)**
   - Annualized protocol fees
   - Represents "tax revenue"
   - Indicates willingness to pay for blockspace

4. 🔄 **Stablecoins ($S)**
   - Total stablecoin supply
   - Measures external capital integration
   - Indicates trust from traditional finance

5. 📈 **Protocol Market Caps ($P)**
   - Aggregate value of protocol tokens
   - Represents the ecosystem's "industrial base"
   - Measures protocol innovation and adoption

6. 🎨 **Cultural Capital ($C)**
   - NFT market value
   - Represents social and cultural impact
   - Measures soft power and community engagement

## Features

- Real-time calculation of Ethereum's GDP: M + K + F + S + P + C
- 24-hour change tracking for each component
- Interactive visualization of GDP composition
- Automatic data updates every 5 minutes
- Modern, responsive dark mode UI

## Technology Stack

### Backend
- Python/Flask for API integration and calculations
- Advanced caching system for optimal performance
- Multiple data source aggregation

### Frontend
- JavaScript with Chart.js for dynamic visualizations
- Tailwind CSS for modern, responsive design
- Real-time updates and interactive components

### Data Sources
- CoinGecko API for market data
- DeFiLlama API for TVL and protocol metrics
- OpenSea API for NFT valuations

### Author 
Developed with ❤️ by Carles Cerqueda

## Installation

### Prerequisites

- Python 3.9 or higher
- Node.js (for Vercel deployment)
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/HiCarC/ETH_GDP.git
cd ETH_GDP
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
cp .env.example .env

# Edit .env with your API keys:
# COINGECKO_API_KEY=your_key_here
# OPENSEA_API_KEY=your_key_here
```

5. Run the development server:
```bash
python run.py
```

The application will be available at `http://localhost:8000`

### Production Deployment

#### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

3. Configure environment variables:
```bash
vercel env add COINGECKO_API_KEY
vercel env add OPENSEA_API_KEY
```

4. Deploy to production:
```bash
vercel --prod
```

### Updating the Application

To update your deployment:
```bash
git add .
git commit -m "your update message"
git push origin main
```

Vercel will automatically deploy updates when you push to main.

### Troubleshooting

- If you encounter API rate limits, verify your API keys in .env
- For deployment issues, check Vercel logs: `vercel logs`
- For local development issues, check Flask debug output

## API Configuration

[API configuration details...]

## Contributing

Contributions are welcome! This project aims to advance the understanding of blockchain economies through better metrics and visualizations.

## Author

Developed with ❤️ by Carles Cerqueda