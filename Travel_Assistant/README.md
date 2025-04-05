# AI Travel Assistant

An intelligent travel planning assistant powered by Google's Gemini AI. This application helps users plan their trips by providing personalized recommendations, generating detailed itineraries, and answering travel-related questions.

## Features

- **Smart Conversation Interface**: Natural language processing to understand travel preferences
- **Personalized Travel Planning**: Customized recommendations based on user preferences
- **Detailed Itinerary Generation**: Day-by-day travel plans with activities, timings, and costs
- **Advanced Pattern Recognition**: Enhanced understanding of travel-related queries including:
  - Multiple destination patterns (e.g., "trip to", "visit", "going to", "dreaming about")
  - Flexible duration recognition (days, nights, weeks, months)
  - Comprehensive budget parsing (multiple currencies and formats)
  - Interest and travel style detection

## Prerequisites

- Python 3.8 or higher
- Google API key for Gemini AI
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travel-assistant.git
cd travel-assistant
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Google API key:
```bash
# On Windows
set GOOGLE_API_KEY=your-api-key-here

# On Linux/Mac
export GOOGLE_API_KEY=your-api-key-here
```

## Usage

1. Run the application:
```bash
python travel_assistant.py
```

2. Access the web interface at `http://localhost:7860`

3. Start chatting with the travel assistant about your travel plans!

## Features in Detail

### Smart Conversation
- Natural language understanding of travel preferences
- Context-aware responses
- Memory of previous conversations
- Real-time preference updates

### Travel Planning
- Destination suggestions
- Duration recommendations
- Budget planning
- Activity recommendations
- Local insights and tips

### Itinerary Generation
- Detailed day-by-day plans
- Morning, afternoon, and evening activities
- Restaurant and dining recommendations
- Transportation options
- Cost estimates
- Local customs and etiquette

## Supported Queries

The assistant understands various ways of expressing travel preferences:

### Destinations
- "I want to go to Paris"
- "Planning a trip to Japan"
- "Dreaming about Bali"
- "Interested in New York"
- "Looking for beach destinations"

### Duration
- "For 5 days"
- "2 weeks trip"
- "Spend 3 nights"
- "One month vacation"
- "Week-long stay"

### Budget
- "$1000 budget"
- "₹50000 for the trip"
- "Around 2000 euros"
- "Budget of 1 lakh"
- "2 crores for luxury travel"

## Technical Details

- Built with Gradio for the web interface
- Powered by Google's Gemini 2.0 Flash Lite model
- Advanced regex patterns for preference extraction
- Real-time response generation
- Safety filters for appropriate content

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for the language model
- Gradio for the web interface
- The open-source community for various utilities and tools 