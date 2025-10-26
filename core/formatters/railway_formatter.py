"""
Railway information formatter for Indian Railways.
Formats train schedules, PNR status, and railway data.
"""

from typing import Dict, Any, List
from .base_formatter import ResponseFormatter


class RailwayFormatter(ResponseFormatter):
    """Format Indian Railway information"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format railway data.
        
        Args:
            data: Railway data dictionary
            
        Returns:
            Formatted railway information
        """
        if not data or data.get('error'):
            return self.format_no_data("No railway information available")
        
        response = self.add_header("Indian Railway Information", self.emojis['railway'])
        
        # Single train details
        if 'train_number' in data:
            response += self._format_train_details(data)
        
        # Popular trains from location
        if 'popular_trains_from_muzaffarnagar' in data:
            response += self._format_popular_trains(data['popular_trains_from_muzaffarnagar'])
        
        # PNR status
        if 'pnr_status' in data:
            response += self._format_pnr_status(data['pnr_status'])
        
        # Station information
        if 'station_info' in data:
            response += self._format_station_info(data['station_info'])
        
        # Add note if available
        if data.get('note'):
            response += f"\nℹ️  **Note:** {data['note']}\n"
        
        response += self.add_footer("Railway information for India")
        
        return response
    
    def _format_train_details(self, train_data: Dict[str, Any]) -> str:
        """Format single train details"""
        section = self.add_section("Train Details", "🚆")
        
        details = [
            ("Train Number", train_data.get('train_number', 'N/A')),
            ("Train Name", train_data.get('train_name', 'N/A')),
            ("Route", train_data.get('route', 'N/A')),
            ("Departure Time", train_data.get('departure_time', 'N/A')),
            ("Arrival Time", train_data.get('arrival_time', 'N/A')),
            ("Running Days", train_data.get('running_days', 'N/A')),
            ("Distance", train_data.get('distance', 'N/A')),
            ("Duration", train_data.get('duration', 'N/A'))
        ]
        
        for label, value in details:
            if value and value != 'N/A':
                section += f"  • **{label}:** {value}\n"
        
        # Add class information if available
        if train_data.get('classes'):
            section += f"\n**Available Classes:**\n"
            classes = train_data['classes']
            if isinstance(classes, list):
                section += self.format_list_items(classes)
            else:
                section += f"  • {classes}\n"
        
        section += "\n"
        return section
    
    def _format_popular_trains(self, popular_trains: List[str]) -> str:
        """Format popular trains list"""
        section = self.add_section("Popular Trains from Muzaffarnagar", "🚉")
        
        if not popular_trains:
            section += "No popular trains data available\n\n"
            return section
        
        section += "**Frequently Used Trains:**\n"
        for train in popular_trains[:10]:  # Limit to 10
            section += f"  • Train {train}\n"
        
        if len(popular_trains) > 10:
            section += f"  ... and {len(popular_trains) - 10} more trains\n"
        
        section += "\n"
        return section
    
    def _format_pnr_status(self, pnr_data: Dict[str, Any]) -> str:
        """Format PNR status information"""
        section = self.add_section("PNR Status", "🎫")
        
        if pnr_data.get('error'):
            section += f"❌ Error: {pnr_data['error']}\n\n"
            return section
        
        # Basic PNR info
        pnr_details = [
            ("PNR Number", pnr_data.get('pnr', 'N/A')),
            ("Train Number", pnr_data.get('train_number', 'N/A')),
            ("Train Name", pnr_data.get('train_name', 'N/A')),
            ("Journey Date", pnr_data.get('journey_date', 'N/A')),
            ("From Station", pnr_data.get('from_station', 'N/A')),
            ("To Station", pnr_data.get('to_station', 'N/A')),
            ("Class", pnr_data.get('class', 'N/A')),
            ("Chart Status", pnr_data.get('chart_status', 'N/A'))
        ]
        
        for label, value in pnr_details:
            if value and value != 'N/A':
                section += f"  • **{label}:** {value}\n"
        
        # Passenger details
        if pnr_data.get('passengers'):
            section += f"\n**Passenger Details:**\n"
            for i, passenger in enumerate(pnr_data['passengers'], 1):
                section += f"  {i}. {passenger.get('name', 'N/A')} - "
                section += f"Status: {passenger.get('status', 'N/A')}\n"
        
        section += "\n"
        return section
    
    def _format_station_info(self, station_data: Dict[str, Any]) -> str:
        """Format station information"""
        section = self.add_section("Station Information", "🏢")
        
        station_details = [
            ("Station Name", station_data.get('name', 'N/A')),
            ("Station Code", station_data.get('code', 'N/A')),
            ("State", station_data.get('state', 'N/A')),
            ("Zone", station_data.get('zone', 'N/A')),
            ("Division", station_data.get('division', 'N/A'))
        ]
        
        for label, value in station_details:
            if value and value != 'N/A':
                section += f"  • **{label}:** {value}\n"
        
        # Platform information
        if station_data.get('platforms'):
            section += f"  • **Platforms:** {station_data['platforms']}\n"
        
        section += "\n"
        return section
    
    def format_railway_error(self, error: str, query_type: str = "railway") -> str:
        """
        Format railway data error.
        
        Args:
            error: Error message
            query_type: Type of railway query
            
        Returns:
            Formatted error message
        """
        response = self.add_header(f"{query_type.title()} Error", self.emojis['error'])
        response += f"❌ Failed to retrieve {query_type} information\n\n"
        response += f"Error: {error}\n\n"
        
        # Add helpful suggestions
        suggestions = [
            "Check if the train number is correct",
            "Verify the PNR number format",
            "Try again after some time",
            "Contact railway customer service if the issue persists"
        ]
        
        response += "**Suggestions:**\n"
        response += self.format_list_items(suggestions)
        response += "\n"
        
        response += self.add_footer("Please try again later")
        
        return response