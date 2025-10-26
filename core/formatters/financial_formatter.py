"""
Financial data formatter for Indian markets.
Formats cryptocurrency, currency rates, and mutual fund data.
"""

from typing import Dict, Any
from .base_formatter import ResponseFormatter


class FinancialFormatter(ResponseFormatter):
    """Format Indian financial data (INR focus)"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format financial data.
        
        Args:
            data: Financial data dictionary
            
        Returns:
            Formatted financial information
        """
        if not data or all(section.get('error') for section in data.values()):
            return self.format_no_data("No financial data available")
        
        response = self.add_header("Indian Financial Data (INR)", self.emojis['finance'])
        
        # Cryptocurrency section
        if 'cryptocurrency' in data and not data['cryptocurrency'].get('error'):
            response += self._format_cryptocurrency(data['cryptocurrency'])
        
        # Currency rates section
        if 'currency_rates' in data and not data['currency_rates'].get('error'):
            response += self._format_currency_rates(data['currency_rates'])
        
        # Mutual funds section
        if 'mutual_funds' in data and not data['mutual_funds'].get('error'):
            response += self._format_mutual_funds(data['mutual_funds'])
        
        response += self.add_footer("Financial data for India")
        
        return response
    
    def _format_cryptocurrency(self, crypto_data: Dict[str, Any]) -> str:
        """Format cryptocurrency prices"""
        section = self.add_section("Cryptocurrency Prices", "₿")
        
        # Bitcoin data
        section += "**Bitcoin (BTC):**\n"
        section += f"  • Price in INR: ₹{crypto_data.get('price_inr', 'N/A'):,.2f}\n"
        section += f"  • Price in USD: ${crypto_data.get('price_usd', 'N/A'):,.2f}\n"
        
        # Additional crypto data if available
        if crypto_data.get('change_24h'):
            change = crypto_data['change_24h']
            change_emoji = "📈" if change >= 0 else "📉"
            section += f"  • 24h Change: {change_emoji} {change:+.2f}%\n"
        
        if crypto_data.get('market_cap'):
            section += f"  • Market Cap: ${crypto_data['market_cap']:,.0f}\n"
        
        section += f"  • Last Updated: {crypto_data.get('updated', 'N/A')}\n\n"
        
        return section
    
    def _format_currency_rates(self, rates_data: Dict[str, Any]) -> str:
        """Format currency exchange rates"""
        section = self.add_section("Currency Exchange Rates (Base: INR)", "💱")
        
        rates = rates_data.get('rates', {})
        if not rates:
            section += "No exchange rates available\n\n"
            return section
        
        # Format major currencies
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
        
        for currency in major_currencies:
            if currency in rates:
                rate = rates[currency]
                section += f"  • 1 INR = {rate:.4f} {currency}\n"
        
        # Add other currencies if available
        other_currencies = {k: v for k, v in rates.items() if k not in major_currencies}
        if other_currencies:
            section += "\n**Other Currencies:**\n"
            for currency, rate in list(other_currencies.items())[:5]:  # Limit to 5
                section += f"  • 1 INR = {rate:.4f} {currency}\n"
        
        section += f"\n  • Updated: {rates_data.get('updated', 'N/A')}\n\n"
        
        return section
    
    def _format_mutual_funds(self, mf_data: Dict[str, Any]) -> str:
        """Format mutual fund information"""
        section = self.add_section("Mutual Fund NAV", "📈")
        
        # Single fund details
        if 'scheme_name' in mf_data:
            section += self._format_single_fund(mf_data)
        
        # Multiple fund matches
        elif 'matches' in mf_data:
            section += self._format_fund_matches(mf_data['matches'])
        
        # Popular funds
        elif 'popular_funds' in mf_data:
            section += self._format_popular_funds(mf_data['popular_funds'])
        
        else:
            section += "No mutual fund data available\n"
        
        section += "\n"
        return section
    
    def _format_single_fund(self, fund_data: Dict[str, Any]) -> str:
        """Format single mutual fund details"""
        details = f"**Fund Details:**\n"
        details += f"  • Scheme Name: {fund_data.get('scheme_name', 'N/A')}\n"
        details += f"  • Scheme Code: {fund_data.get('scheme_code', 'N/A')}\n"
        details += f"  • Fund House: {fund_data.get('fund_house', 'N/A')}\n"
        details += f"  • Scheme Type: {fund_data.get('scheme_type', 'N/A')}\n"
        details += f"  • NAV: ₹{fund_data.get('nav', 'N/A')}\n"
        details += f"  • Date: {fund_data.get('date', 'N/A')}\n"
        details += f"  • Currency: {fund_data.get('currency', 'INR')}\n"
        
        return details
    
    def _format_fund_matches(self, matches: list) -> str:
        """Format multiple fund search results"""
        if not matches:
            return "No matching funds found\n"
        
        details = f"**Search Results ({len(matches)} matches):**\n"
        for match in matches[:10]:  # Limit to 10 results
            name = match.get('name', 'Unknown')
            code = match.get('code', 'N/A')
            nav = match.get('nav', 'N/A')
            details += f"  • {name} (Code: {code}) - NAV: ₹{nav}\n"
        
        if len(matches) > 10:
            details += f"  ... and {len(matches) - 10} more results\n"
        
        return details
    
    def _format_popular_funds(self, popular_funds: list) -> str:
        """Format popular mutual funds"""
        if not popular_funds:
            return "No popular funds data available\n"
        
        details = "**Popular Mutual Funds:**\n"
        for fund in popular_funds[:10]:  # Limit to 10
            name = fund.get('name', 'Unknown')
            code = fund.get('code', 'N/A')
            nav = fund.get('nav', 'N/A')
            details += f"  • {name} (Code: {code}) - NAV: ₹{nav}\n"
        
        return details
    
    def format_financial_error(self, error: str, data_type: str = "financial") -> str:
        """
        Format financial data error.
        
        Args:
            error: Error message
            data_type: Type of financial data
            
        Returns:
            Formatted error message
        """
        response = self.add_header(f"{data_type.title()} Data Error", self.emojis['error'])
        response += f"❌ Failed to retrieve {data_type} data\n\n"
        response += f"Error: {error}\n"
        response += self.add_footer("Please try again later")
        
        return response