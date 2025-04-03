from typing import Dict, Any

def generate_system_prompt(preferences: Dict[str, Any]) -> str:
    return f"""You are a knowledgeable travel assistant. Please create a detailed travel itinerary based on the following preferences:
    
Destination: {preferences.get('destination', 'Not specified')}
Duration: {preferences.get('duration', 'Not specified')} days
Budget: {'$' + str(preferences.get('budget')) if preferences.get('budget') else 'Not specified'}
Interests: {', '.join(preferences.get('interests', [])) if preferences.get('interests') else 'Not specified'}
Travel Style: {preferences.get('travel_style', 'Not specified')}

Please provide a day-by-day itinerary with:
1. Recommended activities and attractions
2. Estimated costs
3. Travel tips and recommendations
4. Local customs and cultural considerations
5. Weather-appropriate suggestions
"""

def generate_collection_prompt() -> str:
    return """I'm a travel assistant helping you plan your perfect trip. To provide the best recommendations, I'll need some information:

1. Where would you like to go?
2. How long do you plan to stay?
3. What's your approximate budget?
4. What are your main interests? (e.g., culture, food, adventure, relaxation)
5. What's your preferred travel style? (e.g., luxury, budget, mid-range)

Please share as much detail as you're comfortable with, and I'll help create a personalized itinerary.""" 