# API Examples

## Using cURL

### 1. Health Check

```bash
curl http://localhost:5000/api/v1/health
```

### 2. Create Ethereum Wallet

```bash
curl -X POST http://localhost:5000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "chain": "ethereum",
    "label": "My Main ETH Wallet"
  }'
```

### 3. Create Solana Wallet

```bash
curl -X POST http://localhost:5000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "chain": "solana",
    "label": "My SOL Wallet"
  }'
```

### 4. Create Cosmos Hub Wallet

```bash
curl -X POST http://localhost:5000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "cosmos1example1234567890abcdefghijklmnopqrs",
    "chain": "cosmos",
    "label": "My Cosmos Wallet"
  }'
```

### 5. Create Celestia Wallet

```bash
curl -X POST http://localhost:5000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "celestia1example1234567890abcdefghijklmnopqrs",
    "chain": "celestia",
    "label": "My Celestia Wallet"
  }'
```

### 6. Create Starknet Wallet

```bash
curl -X POST http://localhost:5000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "chain": "starknet",
    "label": "My Starknet Wallet"
  }'
```

### 7. Get All Wallets

```bash
curl http://localhost:5000/api/v1/wallets
```

### 8. Fetch Wallet Balances

```bash
# Get wallet ID from previous response
WALLET_ID="your-wallet-uuid-here"

curl -X POST http://localhost:5000/api/v1/wallets/$WALLET_ID/fetch \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": false}'
```

### 9. Get Stored Balances

```bash
curl http://localhost:5000/api/v1/wallets/$WALLET_ID/balances
```

### 10. Get Portfolio Summary

```bash
curl http://localhost:5000/api/v1/portfolio
```

### 11. Get Balance History

```bash
curl "http://localhost:5000/api/v1/portfolio/history?wallet_id=$WALLET_ID&limit=50"
```

## Using Python

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Create wallet
response = requests.post(
    f"{BASE_URL}/wallets",
    json={
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "chain": "ethereum",
        "label": "My ETH Wallet"
    }
)
wallet = response.json()["data"]
wallet_id = wallet["id"]
print(f"Created wallet: {wallet_id}")

# Fetch balances
response = requests.post(
    f"{BASE_URL}/wallets/{wallet_id}/fetch",
    json={"force_refresh": True}
)
balances = response.json()["data"]
print(f"Balances: {balances}")

# Get portfolio
response = requests.get(f"{BASE_URL}/portfolio")
portfolio = response.json()["data"]
print(f"Total value: ${portfolio['total_usd_value']}")
```

## Using JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api/v1';

async function createWallet() {
  try {
    const response = await axios.post(`${BASE_URL}/wallets`, {
      address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      chain: 'ethereum',
      label: 'My ETH Wallet'
    });
    
    const wallet = response.data.data;
    console.log('Created wallet:', wallet.id);
    return wallet.id;
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

async function fetchBalances(walletId) {
  try {
    const response = await axios.post(
      `${BASE_URL}/wallets/${walletId}/fetch`,
      { force_refresh: true }
    );
    
    console.log('Balances:', response.data.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

async function getPortfolio() {
  try {
    const response = await axios.get(`${BASE_URL}/portfolio`);
    const portfolio = response.data.data;
    
    console.log(`Total wallets: ${portfolio.total_wallets}`);
    console.log(`Total value: $${portfolio.total_usd_value}`);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

// Run
(async () => {
  const walletId = await createWallet();
  if (walletId) {
    await fetchBalances(walletId);
    await getPortfolio();
  }
})();
```

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Crypto Portfolio Tracker",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Create Wallet",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb\",\n  \"chain\": \"ethereum\",\n  \"label\": \"My Main Wallet\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/wallets",
          "host": ["{{base_url}}"],
          "path": ["wallets"]
        }
      }
    },
    {
      "name": "Get Portfolio",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/portfolio",
          "host": ["{{base_url}}"],
          "path": ["portfolio"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000/api/v1"
    }
  ]
}
```
