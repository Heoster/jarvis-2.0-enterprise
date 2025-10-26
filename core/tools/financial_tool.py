"""
Financial data tool for Indian markets.
Standardized interface for financial operations.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool, ToolResult
from core.indian_apis import get_indian_api


class FinancialTool(BaseTool):
    """Financial data tool with standardized interface"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.indian_api = None
    
    async def _ensure_api(self):
        """Ensure Indian API is initialized"""
        if self.indian_api is None:
            self.indian_api = await get_indian_api()
    
    def get_required_fields(self) -> List[str]:
        """Get required input fields"""
        return ['data_type']
    
    def get_optional_fields(self) -> List[str]:
        """Get optional input fields"""
        return ['currency', 'symbol', 'fund_code', 'search_term']
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        if 'data_type' not in input_data:
            return False
        
        data_type = input_data['data_type']
        valid_types = ['cryptocurrency', 'currency_rates', 'mutual_funds', 'financial_summary']
        
        if data_type not in valid_types:
            return False
        
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute financial data retrieval.
        
        Args:
            input_data: Financial parameters
                - data_type (str): Type of financial data
                - currency (str, optional): Currency code
                - symbol (str, optional): Cryptocurrency symbol
                - fund_code (str, optional): Mutual fund code
                - search_term (str, optional): Search term for funds
        
        Returns:
            ToolResult with financial data
        """
        try:
            await self._ensure_api()
            
            data_type = input_data['data_type']
            
            self.logger.info(f"Fetching financial data: {data_type}")
            
            # Route to appropriate financial operation
            if data_type == 'cryptocurrency':
                result = await self._get_cryptocurrency_data(input_data)
            elif data_type == 'currency_rates':
                result = await self._get_currency_rates(input_data)
            elif data_type == 'mutual_funds':
                result = await self._get_mutual_fund_data(input_data)
            elif data_type == 'financial_summary':
                result = await self._get_financial_summary()
            else:
                return self._create_error_result(f"Unknown data type: {data_type}")
            
            if result and not result.get('error'):
                metadata = {
                    'data_type': data_type,
                    'currency': 'INR',  # Default to INR for Indian markets
                    'source': 'Indian APIs'
                }
                
                return self._create_success_result(result, metadata)
            else:
                error_msg = result.get('error', 'Financial data retrieval failed') if result else 'No data returned'
                return self._create_error_result(error_msg)
                
        except Exception as e:
            self.logger.error(f"Financial data retrieval failed: {e}")
            return self._create_error_result(str(e))
    
    async def _get_cryptocurrency_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get cryptocurrency data"""
        # For now, get Bitcoin data - could be extended for other cryptocurrencies
        financial_summary = await self.indian_api.get_financial_summary()
        
        if financial_summary and 'cryptocurrency' in financial_summary:
            return financial_summary['cryptocurrency']
        
        return {'error': 'Cryptocurrency data not available'}
    
    async def _get_currency_rates(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get currency exchange rates"""
        financial_summary = await self.indian_api.get_financial_summary()
        
        if financial_summary and 'currency_rates' in financial_summary:
            return financial_summary['currency_rates']
        
        return {'error': 'Currency rates not available'}
    
    async def _get_mutual_fund_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mutual fund data"""
        fund_code = input_data.get('fund_code')
        search_term = input_data.get('search_term')
        
        if fund_code:
            # Get specific fund data
            return await self.indian_api.get_mutual_fund_nav(fund_code)
        elif search_term:
            # Search for funds
            return await self.indian_api.search_mutual_funds(search_term)
        else:
            # Get general mutual fund info
            return await self.indian_api.get_mutual_fund_info()
    
    async def _get_financial_summary(self) -> Dict[str, Any]:
        """Get complete financial summary"""
        return await self.indian_api.get_financial_summary()
    
    async def get_bitcoin_price(self) -> ToolResult:
        """
        Get Bitcoin price in INR.
        
        Returns:
            ToolResult with Bitcoin price data
        """
        return await self.execute({
            'data_type': 'cryptocurrency',
            'symbol': 'BTC'
        })
    
    async def get_currency_rates(self, base_currency: str = 'INR') -> ToolResult:
        """
        Get currency exchange rates.
        
        Args:
            base_currency: Base currency (default: INR)
            
        Returns:
            ToolResult with exchange rates
        """
        return await self.execute({
            'data_type': 'currency_rates',
            'currency': base_currency
        })
    
    async def get_mutual_fund_nav(self, fund_code: str) -> ToolResult:
        """
        Get mutual fund NAV by code.
        
        Args:
            fund_code: Mutual fund scheme code
            
        Returns:
            ToolResult with NAV data
        """
        return await self.execute({
            'data_type': 'mutual_funds',
            'fund_code': fund_code
        })
    
    async def search_mutual_funds(self, search_term: str) -> ToolResult:
        """
        Search for mutual funds.
        
        Args:
            search_term: Search term
            
        Returns:
            ToolResult with search results
        """
        return await self.execute({
            'data_type': 'mutual_funds',
            'search_term': search_term
        })
    
    async def get_financial_summary(self) -> ToolResult:
        """
        Get complete financial summary.
        
        Returns:
            ToolResult with financial summary
        """
        return await self.execute({
            'data_type': 'financial_summary'
        })
    
    async def health_check(self) -> bool:
        """Check if financial APIs are working"""
        try:
            await self._ensure_api()
            # Try to get a simple financial summary
            result = await self.indian_api.get_financial_summary()
            return result is not None and not result.get('error')
        except Exception as e:
            self.logger.error(f"Financial tool health check failed: {e}")
            return False