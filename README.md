# AI Travel Assistant

An intelligent travel planning assistant powered by LLMs that helps users plan their trips by providing personalized recommendations and itineraries.

## Features

- Interactive chat interface for travel planning
- Automatic extraction of travel preferences
- Personalized itinerary generation
- Real-time preference tracking
- Support for both API-based and local LLM models

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd travel-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```env
HF_API_TOKEN=your_huggingface_token
```

## Usage

1. Run the Gradio app:
```bash
python -m app.gradio_app
```

2. Open your browser and navigate to:
- Local URL: http://127.0.0.1:7861
- Or use the public URL provided by Gradio

3. Start chatting with the assistant:
- Describe your travel plans
- The assistant will automatically extract preferences
- Generate detailed itineraries based on your preferences

## Project Structure 

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 