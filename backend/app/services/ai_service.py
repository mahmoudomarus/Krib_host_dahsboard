"""
AI Service for automated property listing generation
"""

import openai
import anthropic
from typing import Dict, List, Optional, Any
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize OpenAI if API key is available
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
        
        # Initialize Anthropic if API key is available
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    async def generate_property_description(
        self,
        property_data: Dict[str, Any],
        use_anthropic: bool = False
    ) -> Dict[str, str]:
        """
        Generate compelling property description using AI
        
        Args:
            property_data: Basic property information
            use_anthropic: Whether to use Anthropic Claude instead of OpenAI
            
        Returns:
            Dict with generated description and suggestions
        """
        try:
            # Prepare the context
            context = self._prepare_property_context(property_data)
            
            if use_anthropic and self.anthropic_client:
                return await self._generate_with_anthropic(context)
            elif self.openai_client:
                return await self._generate_with_openai(context)
            else:
                # Fallback to template-based description
                return self._generate_fallback_description(property_data)
                
        except Exception as e:
            logger.error(f"AI description generation failed: {e}")
            return self._generate_fallback_description(property_data)
    
    async def generate_amenities_suggestions(
        self,
        property_data: Dict[str, Any],
        existing_amenities: List[str] = None
    ) -> List[str]:
        """
        Generate smart amenities suggestions based on property type and location
        """
        try:
            if existing_amenities is None:
                existing_amenities = []
            
            # Base amenities by property type
            base_amenities = self._get_base_amenities(property_data.get('property_type', 'apartment'))
            
            # AI-enhanced suggestions
            if self.openai_client:
                ai_suggestions = await self._get_ai_amenities_suggestions(property_data)
                base_amenities.extend(ai_suggestions)
            
            # Remove duplicates and existing amenities
            suggested = list(set(base_amenities) - set(existing_amenities))
            
            # Return top 10 suggestions
            return suggested[:10]
            
        except Exception as e:
            logger.error(f"Amenities suggestion failed: {e}")
            return self._get_base_amenities(property_data.get('property_type', 'apartment'))[:5]
    
    async def optimize_listing_title(
        self,
        original_title: str,
        property_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate optimized title variations for better search visibility
        """
        try:
            if self.openai_client:
                return await self._optimize_title_with_ai(original_title, property_data)
            else:
                return self._generate_title_variations(original_title, property_data)
                
        except Exception as e:
            logger.error(f"Title optimization failed: {e}")
            return [original_title]
    
    async def generate_pricing_strategy(
        self,
        property_data: Dict[str, Any],
        market_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered pricing recommendations
        """
        try:
            base_price = property_data.get('price_per_night', 100)
            
            # Calculate dynamic pricing suggestions
            strategy = {
                'base_price': base_price,
                'weekend_multiplier': 1.2,
                'seasonal_adjustments': {
                    'winter': 0.8,
                    'spring': 1.0,
                    'summer': 1.3,
                    'fall': 1.1
                },
                'suggested_range': {
                    'min': round(base_price * 0.7),
                    'max': round(base_price * 1.5)
                },
                'recommendations': []
            }
            
            if self.openai_client and market_data:
                ai_insights = await self._get_ai_pricing_insights(property_data, market_data)
                strategy['recommendations'].extend(ai_insights)
            
            return strategy
            
        except Exception as e:
            logger.error(f"Pricing strategy generation failed: {e}")
            return {'base_price': property_data.get('price_per_night', 100)}
    
    # Private methods
    
    def _prepare_property_context(self, property_data: Dict[str, Any]) -> str:
        """Prepare context string for AI generation"""
        return f"""
        Property Type: {property_data.get('property_type', 'apartment').title()}
        Location: {property_data.get('city', '')}, {property_data.get('state', '')}
        Bedrooms: {property_data.get('bedrooms', 0)}
        Bathrooms: {property_data.get('bathrooms', 0)}
        Max Guests: {property_data.get('max_guests', 0)}
        Price per Night: ${property_data.get('price_per_night', 0)}
        Existing Amenities: {', '.join(property_data.get('amenities', []))}
        Additional Notes: {property_data.get('additional_notes', '')}
        """
    
    async def _generate_with_openai(self, context: str) -> Dict[str, str]:
        """Generate description using OpenAI GPT"""
        try:
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in writing compelling vacation rental descriptions. 
                        Create engaging, detailed descriptions that highlight unique features and create emotional connection.
                        Focus on the experience guests will have, not just listing features.
                        Write in a warm, welcoming tone that makes guests excited to book."""
                    },
                    {
                        "role": "user",
                        "content": f"""Create a compelling property description for this rental property:
                        
                        {context}
                        
                        Please provide:
                        1. A main description (2-3 paragraphs)
                        2. A short summary (1-2 sentences)
                        3. Key highlights (3-5 bullet points)
                        
                        Format as JSON with keys: description, summary, highlights"""
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"description": content, "summary": "", "highlights": []}
                
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def _generate_with_anthropic(self, context: str) -> Dict[str, str]:
        """Generate description using Anthropic Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=800,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are an expert in writing compelling vacation rental descriptions. 
                        Create an engaging, detailed description for this property:
                        
                        {context}
                        
                        Please provide a JSON response with:
                        - description: 2-3 paragraph compelling description
                        - summary: 1-2 sentence summary
                        - highlights: Array of 3-5 key features
                        
                        Focus on the guest experience and emotional appeal."""
                    }
                ]
            )
            
            content = response.content[0].text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"description": content, "summary": "", "highlights": []}
                
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    def _generate_fallback_description(self, property_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate basic description without AI"""
        property_type = property_data.get('property_type', 'property').title()
        bedrooms = property_data.get('bedrooms', 0)
        bathrooms = property_data.get('bathrooms', 0)
        max_guests = property_data.get('max_guests', 1)
        city = property_data.get('city', 'a great location')
        
        description = f"""Welcome to this beautiful {property_type.lower()} in {city}! 
        
        This comfortable space features {bedrooms} bedroom{'s' if bedrooms != 1 else ''} and {bathrooms} bathroom{'s' if bathrooms != 1 else ''}, 
        perfect for up to {max_guests} guest{'s' if max_guests != 1 else ''}. 
        
        Whether you're here for business or leisure, you'll find everything you need for a memorable stay. 
        The space is thoughtfully designed to provide comfort and convenience throughout your visit."""
        
        return {
            "description": description,
            "summary": f"Comfortable {property_type.lower()} for {max_guests} guests in {city}",
            "highlights": [
                f"{bedrooms} bedroom{'s' if bedrooms != 1 else ''}",
                f"{bathrooms} bathroom{'s' if bathrooms != 1 else ''}",
                f"Accommodates {max_guests} guest{'s' if max_guests != 1 else ''}",
                "Great location",
                "Comfortable amenities"
            ]
        }
    
    def _get_base_amenities(self, property_type: str) -> List[str]:
        """Get base amenities based on property type"""
        base_amenities = {
            'apartment': ['WiFi', 'Kitchen', 'Air Conditioning', 'Heating', 'TV'],
            'house': ['WiFi', 'Kitchen', 'Washer/Dryer', 'Parking', 'Garden', 'TV'],
            'condo': ['WiFi', 'Kitchen', 'Air Conditioning', 'Elevator', 'Pool', 'Gym'],
            'villa': ['WiFi', 'Kitchen', 'Pool', 'Garden', 'Parking', 'BBQ Area'],
            'studio': ['WiFi', 'Kitchenette', 'Air Conditioning', 'TV'],
            'cabin': ['WiFi', 'Kitchen', 'Fireplace', 'Nature Views', 'Parking']
        }
        
        return base_amenities.get(property_type, base_amenities['apartment'])
    
    async def _get_ai_amenities_suggestions(self, property_data: Dict[str, Any]) -> List[str]:
        """Get AI-powered amenities suggestions"""
        # This would call AI API for smart suggestions
        # For now, return contextual suggestions
        suggestions = []
        
        if property_data.get('property_type') == 'house':
            suggestions.extend(['Garden', 'BBQ Area', 'Parking', 'Washer/Dryer'])
        
        if property_data.get('bedrooms', 0) > 2:
            suggestions.extend(['Family Friendly', 'High Chair', 'Pack n Play'])
        
        return suggestions
    
    async def _optimize_title_with_ai(self, title: str, property_data: Dict[str, Any]) -> List[str]:
        """Generate optimized titles using AI"""
        # Simplified implementation
        variations = [
            title,
            f"{title} - Perfect for {property_data.get('max_guests', 1)} Guests",
            f"Beautiful {property_data.get('property_type', 'Property')} - {title}",
            f"{title} in {property_data.get('city', 'Great Location')}"
        ]
        return variations[:3]
    
    def _generate_title_variations(self, title: str, property_data: Dict[str, Any]) -> List[str]:
        """Generate title variations without AI"""
        return [title]
    
    async def _get_ai_pricing_insights(self, property_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[str]:
        """Get AI-powered pricing insights"""
        return [
            "Consider increasing weekend rates by 15-20%",
            "Lower weekday rates to improve occupancy",
            "Seasonal pricing adjustments recommended"
        ]


# Global AI service instance
ai_service = AIService()
