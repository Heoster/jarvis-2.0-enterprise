"""
Indian-Specific APIs Integration
Financial data in INR and geographical data for Muzaffarnagar, UP, India
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)



class IndianFinanceAPI:
    """Indian financial data APIs with INR currency support"""
    
    def __init__(self):
        self.session = None
        self.default_location = {
            'city': 'Muzaffarnagar',
            'state': 'Uttar Pradesh',
            'country': 'India',
            'pincode': '251201'
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_crypto_price_inr(self) -> Dict[str, Any]:
        """Get cryptocurrency prices in INR using CoinDesk API"""
        try:
            session = await self._get_session()
            
            async with session.get('https://api.coindesk.com/v1/bpi/currentprice.json') as response:
                if response.status == 200:
                    data = await response.json()
                    usd_price = data['bpi']['USD']['rate_float']
                    inr_price = usd_price * 83  # Approximate conversion
                    
                    return {
                        'currency': 'Bitcoin',
                        'symbol': 'BTC',
                        'price_inr': round(inr_price, 2),
                        'price_usd': round(usd_price, 2),
                        'updated': data['time']['updated']
                    }
            
            return {'error': 'Failed to fetch crypto prices'}
            
        except Exception as e:
            logger.error(f"Crypto price fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_currency_rates_inr(self) -> Dict[str, Any]:
        """Get currency exchange rates for INR"""
        try:
            session = await self._get_session()
            
            async with session.get('https://api.exchangerate-api.com/v4/latest/INR') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'base': 'INR',
                        'rates': {
                            'USD': round(data['rates'].get('USD', 0.012), 4),
                            'EUR': round(data['rates'].get('EUR', 0.011), 4),
                            'GBP': round(data['rates'].get('GBP', 0.0095), 4),
                            'AED': round(data['rates'].get('AED', 0.044), 4),
                        },
                        'updated': data.get('date', datetime.now().strftime('%Y-%m-%d'))
                    }
            
            return {'base': 'INR', 'rates': {'USD': 0.012, 'EUR': 0.011}, 'note': 'Approximate rates'}
            
        except Exception as e:
            logger.error(f"Currency rates fetch failed: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()



class IndianGeographyAPI:
    """Indian geographical and location-based APIs"""
    
    def __init__(self):
        self.session = None
        self.default_location = {
            'city': 'Muzaffarnagar',
            'state': 'Uttar Pradesh',
            'country': 'India',
            'pincode': '251201',
            'lat': 29.4726,
            'lon': 77.7085
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_pincode_info(self, pincode: str = '251201') -> Dict[str, Any]:
        """Get information about Indian PIN code using Zippopotam API"""
        try:
            session = await self._get_session()
            
            async with session.get(f'https://api.zippopotam.us/in/{pincode}') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    places = data.get('places', [])
                    if places:
                        place = places[0]
                        return {
                            'pincode': pincode,
                            'place_name': place.get('place name', 'N/A'),
                            'state': place.get('state', 'N/A'),
                            'latitude': place.get('latitude', 'N/A'),
                            'longitude': place.get('longitude', 'N/A'),
                            'country': 'India'
                        }
            
            # Fallback for Muzaffarnagar
            if pincode == '251201':
                return {
                    'pincode': '251201',
                    'place_name': 'Muzaffarnagar',
                    'state': 'Uttar Pradesh',
                    'latitude': '29.4726',
                    'longitude': '77.7085',
                    'country': 'India'
                }
            
            return {'error': f'No data found for pincode {pincode}'}
            
        except Exception as e:
            logger.error(f"Pincode info fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_ip_location(self) -> Dict[str, Any]:
        """Get location information based on IP address"""
        try:
            session = await self._get_session()
            
            async with session.get('https://api.ipify.org?format=json') as response:
                if response.status == 200:
                    ip_data = await response.json()
                    ip_address = ip_data.get('ip', 'Unknown')
                    
                    async with session.get(f'https://ipapi.co/{ip_address}/json/') as loc_response:
                        if loc_response.status == 200:
                            loc_data = await loc_response.json()
                            
                            return {
                                'ip': ip_address,
                                'city': loc_data.get('city', 'Unknown'),
                                'region': loc_data.get('region', 'Unknown'),
                                'country': loc_data.get('country_name', 'Unknown'),
                                'postal': loc_data.get('postal', 'Unknown'),
                                'currency': loc_data.get('currency', 'Unknown')
                            }
            
            return {'error': 'Failed to fetch IP location'}
            
        except Exception as e:
            logger.error(f"IP location fetch failed: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()



class IndianDataAPI:
    """Combined Indian data API manager"""
    
    def __init__(self):
        self.finance = IndianFinanceAPI()
        self.geography = IndianGeographyAPI()
        self.railway = IndianRailwayAPI()
        self.mutual_fund = IndianMutualFundAPI()
        self.entertainment = EntertainmentAPI()
        logger.info("Indian Data API manager initialized with Railway, Mutual Funds, and Entertainment APIs")
    
    async def get_financial_summary(self) -> Dict[str, Any]:
        """Get comprehensive financial summary in INR"""
        try:
            crypto = await self.finance.get_crypto_price_inr()
            currency = await self.finance.get_currency_rates_inr()
            
            return {
                'cryptocurrency': crypto,
                'currency_rates': currency,
                'currency': 'INR',
                'location': 'India'
            }
        except Exception as e:
            logger.error(f"Financial summary failed: {e}")
            return {'error': str(e)}
    
    async def get_location_summary(self, pincode: str = '251201') -> Dict[str, Any]:
        """Get comprehensive location summary for Muzaffarnagar"""
        try:
            pincode_info = await self.geography.get_pincode_info(pincode)
            ip_location = await self.geography.get_ip_location()
            
            return {
                'pincode_info': pincode_info,
                'your_location': ip_location,
                'default_location': 'Muzaffarnagar, Uttar Pradesh, India'
            }
        except Exception as e:
            logger.error(f"Location summary failed: {e}")
            return {'error': str(e)}
    
    async def get_railway_info(self, train_number: Optional[str] = None, pnr: Optional[str] = None) -> Dict[str, Any]:
        """Get Indian Railway information"""
        try:
            if pnr:
                return await self.railway.get_pnr_status(pnr)
            elif train_number:
                return await self.railway.get_train_schedule(train_number)
            else:
                return {
                    'service': 'Indian Railway Information',
                    'available_services': ['PNR Status', 'Train Schedule'],
                    'popular_trains_from_muzaffarnagar': ['14511', '14521', '14555']
                }
        except Exception as e:
            logger.error(f"Railway info failed: {e}")
            return {'error': str(e)}
    
    async def get_mutual_fund_info(self, scheme_code: Optional[str] = None, query: Optional[str] = None) -> Dict[str, Any]:
        """Get Indian Mutual Fund NAV information"""
        try:
            if query:
                return await self.mutual_fund.search_mutual_funds(query)
            else:
                return await self.mutual_fund.get_mutual_fund_nav(scheme_code)
        except Exception as e:
            logger.error(f"Mutual fund info failed: {e}")
            return {'error': str(e)}
    
    async def get_entertainment(self, content_type: str = 'joke') -> Dict[str, Any]:
        """Get entertainment content - jokes, images, quotes"""
        try:
            if content_type == 'joke':
                return await self.entertainment.get_random_joke()
            elif content_type == 'programming_joke':
                return await self.entertainment.get_programming_joke()
            elif content_type == 'dog':
                return await self.entertainment.get_random_dog_image()
            elif content_type == 'cat':
                return await self.entertainment.get_random_cat_fact()
            elif content_type == 'quote':
                return await self.entertainment.get_random_quote()
            else:
                return {'error': f'Unknown content type: {content_type}'}
        except Exception as e:
            logger.error(f"Entertainment fetch failed: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close all sessions"""
        await self.finance.close()
        await self.geography.close()
        await self.railway.close()
        await self.mutual_fund.close()
        await self.entertainment.close()


# Singleton instance
_indian_api_instance = None

async def get_indian_api() -> IndianDataAPI:
    """Get or create Indian API instance"""
    global _indian_api_instance
    if _indian_api_instance is None:
        _indian_api_instance = IndianDataAPI()
    return _indian_api_instance



class IndianRailwayAPI:
    """Indian Railway APIs for train information"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_pnr_status(self, pnr: str) -> Dict[str, Any]:
        """
        Get Indian Railway PNR status
        Note: This requires RailwayAPI.com API key
        """
        try:
            # This is a placeholder - actual implementation requires API key
            return {
                'service': 'Indian Railway PNR Status',
                'pnr': pnr,
                'note': 'Railway API requires authentication',
                'suggestion': 'Visit https://railwayapi.com/ for API access',
                'status': 'API key required'
            }
        except Exception as e:
            logger.error(f"PNR status fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_train_schedule(self, train_number: str) -> Dict[str, Any]:
        """
        Get Indian Railway train schedule
        Note: This requires RailwayAPI.com API key
        """
        try:
            # Popular trains from Muzaffarnagar
            popular_trains = {
                '14511': {
                    'name': 'Nauchandi Express',
                    'route': 'Muzaffarnagar - Delhi',
                    'departure': '06:30 AM',
                    'arrival': '09:45 AM',
                    'days': 'Daily'
                },
                '14521': {
                    'name': 'Muzaffarnagar Delhi Express',
                    'route': 'Muzaffarnagar - Delhi',
                    'departure': '08:15 AM',
                    'arrival': '11:30 AM',
                    'days': 'Daily'
                },
                '14555': {
                    'name': 'Bareilly Delhi Express',
                    'route': 'Via Muzaffarnagar',
                    'departure': '10:00 AM',
                    'arrival': '01:15 PM',
                    'days': 'Mon, Wed, Fri'
                }
            }
            
            if train_number in popular_trains:
                train = popular_trains[train_number]
                return {
                    'train_number': train_number,
                    'train_name': train['name'],
                    'route': train['route'],
                    'departure_time': train['departure'],
                    'arrival_time': train['arrival'],
                    'running_days': train['days'],
                    'source': 'Local database (sample data)'
                }
            
            return {
                'service': 'Indian Railway Train Schedule',
                'train_number': train_number,
                'note': 'Railway API requires authentication for live data',
                'suggestion': 'Visit https://railwayapi.com/ for API access',
                'popular_trains_from_muzaffarnagar': list(popular_trains.keys())
            }
        except Exception as e:
            logger.error(f"Train schedule fetch failed: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()


class IndianMutualFundAPI:
    """Indian Mutual Fund NAV API"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_mutual_fund_nav(self, scheme_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get latest NAV of Indian mutual funds from AMFI
        Uses MFAPI - Indian Mutual Fund API (free, no key required)
        """
        try:
            session = await self._get_session()
            
            # Default to popular funds if no code provided
            if not scheme_code:
                scheme_code = '119551'  # SBI Bluechip Fund
            
            url = f'https://api.mfapi.in/mf/{scheme_code}'
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' in data and len(data['data']) > 0:
                        latest = data['data'][0]
                        meta = data.get('meta', {})
                        
                        return {
                            'scheme_code': scheme_code,
                            'scheme_name': meta.get('scheme_name', 'N/A'),
                            'fund_house': meta.get('fund_house', 'N/A'),
                            'scheme_type': meta.get('scheme_type', 'N/A'),
                            'nav': latest.get('nav', 'N/A'),
                            'date': latest.get('date', 'N/A'),
                            'currency': 'INR'
                        }
            
            return {'error': f'No data found for scheme code {scheme_code}'}
            
        except Exception as e:
            logger.error(f"Mutual fund NAV fetch failed: {e}")
            return {'error': str(e)}
    
    async def search_mutual_funds(self, query: str) -> Dict[str, Any]:
        """Search for mutual funds by name"""
        # Popular mutual funds for quick reference
        popular_funds = {
            'sbi bluechip': {'code': '119551', 'name': 'SBI Bluechip Fund'},
            'hdfc top 100': {'code': '119533', 'name': 'HDFC Top 100 Fund'},
            'icici prudential': {'code': '120503', 'name': 'ICICI Prudential Bluechip Fund'},
            'axis bluechip': {'code': '120505', 'name': 'Axis Bluechip Fund'},
            'kotak standard': {'code': '119597', 'name': 'Kotak Standard Multicap Fund'}
        }
        
        query_lower = query.lower()
        matches = []
        
        for key, fund in popular_funds.items():
            if query_lower in key:
                matches.append(fund)
        
        if matches:
            return {
                'query': query,
                'matches': matches,
                'note': 'Use scheme code to get NAV details'
            }
        
        return {
            'query': query,
            'matches': [],
            'popular_funds': list(popular_funds.values()),
            'note': 'No matches found. Showing popular funds.'
        }
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()


class EntertainmentAPI:
    """Entertainment APIs - Jokes, Images, Quotes"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_random_joke(self) -> Dict[str, Any]:
        """Get a random joke from Official Joke API"""
        try:
            session = await self._get_session()
            
            async with session.get('https://official-joke-api.appspot.com/random_joke') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'type': data.get('type', 'general'),
                        'setup': data.get('setup', ''),
                        'punchline': data.get('punchline', ''),
                        'id': data.get('id', 0)
                    }
            
            return {'error': 'Failed to fetch joke'}
            
        except Exception as e:
            logger.error(f"Joke fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_programming_joke(self) -> Dict[str, Any]:
        """Get a programming-specific joke"""
        try:
            session = await self._get_session()
            
            async with session.get('https://official-joke-api.appspot.com/jokes/programming/random') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and len(data) > 0:
                        joke = data[0]
                        return {
                            'type': 'programming',
                            'setup': joke.get('setup', ''),
                            'punchline': joke.get('punchline', ''),
                            'id': joke.get('id', 0)
                        }
            
            return {'error': 'Failed to fetch programming joke'}
            
        except Exception as e:
            logger.error(f"Programming joke fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_random_dog_image(self) -> Dict[str, Any]:
        """Get a random dog image from Dog CEO API"""
        try:
            session = await self._get_session()
            
            async with session.get('https://dog.ceo/api/breeds/image/random') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'image_url': data.get('message', ''),
                        'status': data.get('status', ''),
                        'type': 'dog'
                    }
            
            return {'error': 'Failed to fetch dog image'}
            
        except Exception as e:
            logger.error(f"Dog image fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_random_cat_fact(self) -> Dict[str, Any]:
        """Get a random cat fact from Cat Facts API"""
        try:
            session = await self._get_session()
            
            async with session.get('https://cat-fact.herokuapp.com/facts/random') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        'fact': data.get('text', ''),
                        'type': data.get('type', 'cat'),
                        'upvotes': data.get('upvotes', 0)
                    }
            
            return {'error': 'Failed to fetch cat fact'}
            
        except Exception as e:
            logger.error(f"Cat fact fetch failed: {e}")
            return {'error': str(e)}
    
    async def get_random_quote(self) -> Dict[str, Any]:
        """Get a random inspirational quote"""
        try:
            session = await self._get_session()
            
            # Using ZenQuotes API (free, no key required)
            async with session.get('https://zenquotes.io/api/random') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and len(data) > 0:
                        quote = data[0]
                        return {
                            'quote': quote.get('q', ''),
                            'author': quote.get('a', 'Unknown'),
                            'html': quote.get('h', '')
                        }
            
            return {'error': 'Failed to fetch quote'}
            
        except Exception as e:
            logger.error(f"Quote fetch failed: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
