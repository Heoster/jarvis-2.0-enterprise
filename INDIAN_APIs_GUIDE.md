# Indian APIs Integration Guide

## Overview

Jarvis now includes specialized APIs for Indian users with:
- **Financial data in INR** (Indian Rupees)
- **Geographical data for Muzaffarnagar, Uttar Pradesh**
- **Real-time currency exchange rates**
- **Location-based information**

## Features

✅ **Cryptocurrency Prices in INR** - Bitcoin and other crypto prices
✅ **Currency Exchange Rates** - INR to USD, EUR, GBP, AED, etc.
✅ **PIN Code Information** - Details for any Indian PIN code
✅ **IP-based Location** - Your current location based on IP
✅ **Default Location** - Muzaffarnagar, Uttar Pradesh, India

## How to Use

### Financial Queries

Ask Jarvis about financial data and get results in INR:

```
"what is the bitcoin price in INR"
"show me currency exchange rates for INR"
"what is the current crypto price"
"convert INR to USD"
```

### Geographical Queries

Ask about locations in India:

```
"what is the pincode information for Muzaffarnagar"
"show me my current location"
"what is pincode 251201"
"where is Muzaffarnagar"
```

## Example Output

### Financial Data

```
================================================================================
💰 INDIAN FINANCIAL DATA (INR)
================================================================================

📊 CRYPTOCURRENCY PRICES
--------------------------------------------------------------------------------
Bitcoin (BTC):
  • Price in INR: ₹7,200,000.00
  • Price in USD: $86,747.00
  • Last Updated: Oct 25, 2025

💱 CURRENCY EXCHANGE RATES (Base: INR)
--------------------------------------------------------------------------------
  • 1 INR = 0.0114 USD
  • 1 INR = 0.0098 EUR
  • 1 INR = 0.0086 GBP
  • 1 INR = 0.0418 AED
  • Updated: 2025-10-25

================================================================================
✅ Financial data for India
================================================================================
```

### Geographical Data

```
================================================================================
📍 INDIAN GEOGRAPHICAL DATA
================================================================================

📮 PINCODE INFORMATION
--------------------------------------------------------------------------------
PIN Code: 251201
Place: Muzaffarnagar
State: Uttar Pradesh
Coordinates: 29.4726, 77.7085
Country: India

🌐 YOUR CURRENT LOCATION (Based on IP)
--------------------------------------------------------------------------------
IP Address: XXX.XXX.XXX.XXX
City: Your City
Region: Your State
Country: India
Postal Code: XXXXXX
Currency: INR

================================================================================
✅ Default Location: Muzaffarnagar, Uttar Pradesh, India
================================================================================
```

## APIs Used

### Financial APIs

1. **CoinDesk API** - Bitcoin prices
   - URL: https://api.coindesk.com/v1/bpi/currentprice.json
   - No API key required
   - Converts USD to INR automatically

2. **ExchangeRate API** - Currency rates
   - URL: https://api.exchangerate-api.com/v4/latest/INR
   - No API key required
   - Real-time exchange rates

### Geographical APIs

1. **Zippopotam API** - PIN code information
   - URL: https://api.zippopotam.us/in/{pincode}
   - No API key required
   - Covers all Indian PIN codes

2. **IPify + IPapi** - IP-based location
   - URLs: 
     - https://api.ipify.org (get IP)
     - https://ipapi.co/{ip}/json/ (get location)
   - No API key required
   - Accurate location data

## Default Location

The system is configured for:
- **City**: Muzaffarnagar
- **State**: Uttar Pradesh
- **Country**: India
- **PIN Code**: 251201
- **Coordinates**: 29.4726°N, 77.7085°E

## Keywords that Trigger Indian APIs

### Financial Keywords
- bitcoin, crypto, btc
- currency, exchange rate
- inr, rupee, rupees
- dollar, euro, pound

### Geographical Keywords
- muzaffarnagar
- pincode, pin code
- 251201
- uttar pradesh, up
- my location
- ip address

## Technical Details

### Currency Conversion

- **Base Currency**: INR (Indian Rupee)
- **Supported Currencies**: USD, EUR, GBP, AED, SAR
- **Update Frequency**: Real-time (API dependent)
- **Approximate Rate**: 1 USD ≈ 83 INR (for fallback)

### Location Data

- **Default City**: Muzaffarnagar
- **Default State**: Uttar Pradesh
- **Default PIN**: 251201
- **Coordinates**: 29.4726°N, 77.7085°E

## Testing

### Run the Test Script

```bash
python test_indian_apis.py
```

This will test:
- Bitcoin price in INR
- Currency exchange rates
- PIN code information
- IP-based location

### Manual Testing

Just ask Jarvis:
```
"what is bitcoin price in rupees"
"show currency rates for INR"
"what is pincode 251201"
```

## Troubleshooting

### No Financial Data

1. **Check Internet Connection** - APIs require internet
2. **API Timeout** - Some APIs may be slow
3. **Fallback Data** - System provides approximate rates if API fails

### No Location Data

1. **Check IP Address** - Must have valid public IP
2. **VPN Issues** - VPN may affect location accuracy
3. **Fallback to Default** - System uses Muzaffarnagar as default

### Connection Errors

If you see "Cannot connect to host":
- API server may be temporarily down
- Check your firewall settings
- Try again after a few minutes
- System will use fallback data

## Future Enhancements

Planned improvements:
- [ ] Gold/Silver prices in INR
- [ ] Indian stock market data (NSE/BSE)
- [ ] Mutual fund NAV information
- [ ] Indian Railway train information
- [ ] Weather for Muzaffarnagar
- [ ] More cryptocurrency prices
- [ ] Historical price data
- [ ] Price alerts and notifications

## API Rate Limits

All APIs used are free tier:
- **CoinDesk**: No rate limit
- **ExchangeRate API**: 1500 requests/day
- **Zippopotam**: No rate limit
- **IPify**: No rate limit
- **IPapi**: 1000 requests/day

## Privacy & Security

- **No Personal Data Stored** - Only public information
- **IP Address** - Used only for location lookup
- **No Authentication** - All APIs are public
- **No Tracking** - No user data collected

## Support

If you encounter issues:
1. Check this guide
2. Run test script: `python test_indian_apis.py`
3. Review console logs
4. Check internet connection
5. Try different queries

## Credits

- **CoinDesk** - Cryptocurrency prices
- **ExchangeRate API** - Currency rates
- **Zippopotam** - PIN code data
- **IPify** - IP address lookup
- **IPapi** - IP geolocation
- **Jarvis Team** - Integration & development

---

**Last Updated**: October 2025
**Version**: 1.0
**Status**: ✅ Fully Operational
**Location**: Muzaffarnagar, Uttar Pradesh, India
**Currency**: INR (Indian Rupees)
