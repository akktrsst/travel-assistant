import gradio as gr
import google.generativeai as genai
from typing import List
import re
import os

# Initialize Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model with safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-lite',
    safety_settings=safety_settings
)

# Store conversation history and preferences
class ConversationState:
    def __init__(self):
        self.history = []
        self.current_preferences = {
            "destination": None,
            "duration": None,
            "budget": None,
            "currency": "INR",  # Default currency
            "interests": [],
            "travel_style": None
        }

state = ConversationState()

def update_preferences_display():
    prefs = state.current_preferences
    return f"""
    ### Current Travel Preferences
    - Destination: {prefs['destination'] or 'Not specified'}
    - Duration: {f"{prefs['duration']} days" if prefs['duration'] else 'Not specified'}
    - Budget: {f"{prefs['currency']} {prefs['budget']}" if prefs['budget'] else 'Not specified'}
    - Interests: {', '.join(prefs['interests']) if prefs['interests'] else 'Not specified'}
    - Travel Style: {prefs['travel_style'] or 'Not specified'}
    """

def generate_response(message: str, history: List) -> str:
    try:
        # Prepare the conversation context
        prefs = state.current_preferences
        context = f"""You are a helpful travel assistant. Your role is to help users plan their trips, 
        provide travel recommendations, and answer questions about destinations. Be friendly, informative, 
        and specific in your responses.
        
        Current travel preferences:
        - Destination: {prefs['destination'] or 'Not specified'}
        - Duration: {f"{prefs['duration']} days" if prefs['duration'] else 'Not specified'}
        - Budget: {f"{prefs['currency']} {prefs['budget']}" if prefs['budget'] else 'Not specified'}
        - Interests: {', '.join(prefs['interests']) if prefs['interests'] else 'Not specified'}
        - Travel Style: {prefs['travel_style'] or 'Not specified'}
        
        Previous conversation:
        """
        
        for user_msg, bot_msg in history:
            context += f"User: {user_msg}\nAssistant: {bot_msg}\n"
        
        context += f"User: {message}\nAssistant:"
        
        # Generate response using Gemini
        chat = model.start_chat(history=[])
        response = chat.send_message(
            context,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                top_p=0.95,
                top_k=50,
                max_output_tokens=2048,
                candidate_count=1
            )
        )
        
        if not response.text:
            return "I'm here to help you plan your trip! Could you tell me more about your travel plans?"
        
        return response.text.strip()
    except Exception as e:
        print(f"Error in generate_response: {str(e)}")
        return "I'm here to help you plan your trip! Could you tell me more about your travel plans?"

def process_message(message, history):
    try:
        if not message.strip():
            return history or []
            
        # Generate response
        response = generate_response(message, history)
        
        # Update preferences
        update_preferences(message)
        
        # Return the history in the format Gradio expects
        history = history or []
        history.append((message, response))
        return history
    except Exception as e:
        print(f"Error in process_message: {str(e)}")
        history = history or []
        history.append((message, f"Error: {str(e)}"))
        return history

def update_preferences(message):
    # Simple preference extraction logic
    message = message.lower()
    
    # Extract destination using multiple patterns
    destination_patterns = [
        r"trip (?:to|of|in) ([a-zA-Z\s]+)(?:\s|$)",            # trip to Goa
        r"visit ([a-zA-Z\s]+)(?:\s|$)",                        # visit Goa
        r"going to ([a-zA-Z\s]+)(?:\s|$)",                     # going to Goa
        r"travel to ([a-zA-Z\s]+)(?:\s|$)",                    # travel to Goa
        r"plan a trip (?:to|of|in) ([a-zA-Z\s]+)(?:\s|$)",     # plan a trip to Goa
        r"want to go (?:to )?([a-zA-Z\s]+)(?:\s|$)",           # want to go Goa / want to go to Goa
        r"interested in ([a-zA-Z\s]+)(?:\s|$)",                # interested in Goa
        r"like ([a-zA-Z\s]+)(?:\s|$)",                         # like Goa
        r"love ([a-zA-Z\s]+)(?:\s|$)",                         # love Goa
        r"go ([a-zA-Z\s]+)(?:\s|$)",                           # go Goa
        r"trip for ([a-zA-Z\s]+)(?:\s|$)",                     # trip for Goa
        r"prefer ([a-zA-Z\s]+)(?:\s|$)",                       # prefer Goa
        r"looking for ([a-zA-Z\s]+)(?:\s|$)",                  # looking for Goa
        r"dream(?:ing)? (?:about|of)? ([a-zA-Z\s]+)(?:\s|$)",  # dreaming about Goa / dream Goa
    ]

    
    for pattern in destination_patterns:
        match = re.search(pattern, message)
        if match:
            destination = match.group(1).strip()
            if destination:
                state.current_preferences["destination"] = destination
                break
    
    # Extract duration using multiple patterns
    duration_patterns = [
        # Days
        r"for (\d+)\s*(?:days?|d)",                      # "for 2 days", "for 2d"
        r"(\d+)\s*(?:days?|d)(?:\s|$)",                  # "2 days", "2d"

        # Nights
        r"for (\d+)\s*(?:nights?|n)",                    # "for 2 nights", "for 2n"
        r"(\d+)\s*(?:nights?|n)(?:\s|$)",                # "2 nights", "2n"

        # Weeks
        r"for (\d+)\s*(?:weeks?|w)",                     # "for 2 weeks", "for 2w"
        r"(\d+)\s*(?:weeks?|w)(?:\s|$)",                 # "2 weeks", "2w"

        # Months
        r"for (\d+)\s*(?:months?|mo|mnth|m)",            # "for 2 months", "for 2mo", "for 2m"
        r"(\d+)\s*(?:months?|mo|mnth|m)(?:\s|$)",        # "2 months", "2mo", "2m"

        # Generic phrasing
        r"stay for (\d+)\s*(?:days?|nights?|weeks?|months?)",  # "stay for 2 weeks"
        r"spend (\d+)\s*(?:days?|nights?|weeks?|months?)"      # "spend 5 days"
    ]

    
    for pattern in duration_patterns:
        match = re.search(pattern, message)
        if match:
            try:
                duration = int(match.group(1))
                state.current_preferences["duration"] = duration
                break
            except ValueError:
                pass
    
    # Extract budget
    budget_patterns = [
        r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)",  # $1,000 or $1,000.00
        r"₹(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?)",  # ₹1,00,000
        r"(\d+(?:,\d{3})*(?:\.\d{2})?) dollars?",  # 1,000 dollars
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) rupees?",  # 1,00,000 rupees
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) inr",  # 1,00,000 inr
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) rs",  # 1,00,000 rs
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) lakh",  # 1 lakh
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) lakhs",  # 2 lakhs
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) crore",  # 1 crore
        r"(\d+(?:,\d{2})*(?:,\d{2})*(?:\.\d{2})?) crores",  # 2 crores
        r"budget of (\d+(?:,\d{3})*(?:\.\d{2})?)",  # budget of 1,000
        r"around (\d+(?:,\d{3})*(?:\.\d{2})?)"  # around 1,000
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, message)
        if match:
            try:
                amount = match.group(1).replace(',', '')
                # Convert lakhs and crores to rupees
                if "lakh" in pattern:
                    amount = float(amount) * 100000
                elif "crore" in pattern:
                    amount = float(amount) * 10000000
                else:
                    amount = float(amount)
                
                # Store the amount and currency
                state.current_preferences["budget"] = amount
                state.current_preferences["currency"] = "INR" if "₹" in pattern or "rupees" in pattern or "inr" in pattern or "rs" in pattern or "lakh" in pattern or "crore" in pattern else "USD"
                break
            except ValueError:
                pass
    
    # Extract interests with more comprehensive list
    interests = [
        "culture", "food", "adventure", "relaxation", "shopping", "history", "nature",
        "beach", "mountains", "city", "countryside", "art", "music", "sports",
        "wildlife", "architecture", "local cuisine", "nightlife", "family",
        "romantic", "solo", "group", "luxury", "budget", "mid-range"
    ]
    
    found_interests = []
    for interest in interests:
        if interest in message:
            found_interests.append(interest)
    
    if found_interests:
        state.current_preferences["interests"] = found_interests
    
    # Extract travel style with more options
    styles = {
        "luxury": ["luxury", "premium", "high-end", "5-star", "five star"],
        "budget": ["budget", "cheap", "economy", "low-cost", "affordable"],
        "mid-range": ["mid-range", "moderate", "standard", "comfortable"]
    }
    
    for style, keywords in styles.items():
        if any(keyword in message for keyword in keywords):
            state.current_preferences["travel_style"] = style
            break

def generate_travel_itinerary():
    prefs = state.current_preferences
    
    if not prefs["destination"]:
        return "Please provide a destination first."
    
    try:
        prompt = f"""Create a detailed day-by-day travel itinerary for {prefs['destination']} 
        for {prefs['duration']} days with a budget of {prefs['currency']} {prefs['budget']}.
        
        Create a detailed itinerary that includes:

        For each day:
        1. Morning Activities (9:00 AM - 12:00 PM)
           - Specific places to visit
           - Estimated time at each location
           - Entry fees if any
           - Travel time between locations
        
        2. Lunch Options (12:00 PM - 2:00 PM)
           - Restaurant recommendations
           - Local cuisine to try
           - Estimated cost
        
        3. Afternoon Activities (2:00 PM - 5:00 PM)
           - Specific places to visit
           - Estimated time at each location
           - Entry fees if any
           - Travel time between locations
        
        4. Evening Activities (5:00 PM - 9:00 PM)
           - Dinner options
           - Entertainment or relaxation activities
           - Estimated costs
        
        Additional Information:
        - Total estimated daily cost
        - Transportation options and costs
        - Important tips and recommendations
        - Local customs and etiquette to be aware of
        - Emergency contact numbers if available
        
        Please format the response in a clear, easy-to-read manner with proper spacing and bullet points."""
        
        chat = model.start_chat(history=[])
        response = chat.send_message(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=50,
                max_output_tokens=4096,
                candidate_count=1
            )
        )
        
        if not response.text:
            return "I apologize, but I couldn't generate an itinerary at this time. Please try again later."
        
        return response.text.strip()
    except Exception as e:
        print(f"Error in generate_travel_itinerary: {str(e)}")
        return "I apologize, but I encountered an error while generating the itinerary. Please try again later."

def clear_conversation():
    state.history = []
    state.current_preferences = {
        "destination": None,
        "duration": None,
        "budget": None,
        "currency": "INR",  # Default currency
        "interests": [],
        "travel_style": None
    }
    return [], update_preferences_display()

def create_gradio_interface():
    with gr.Blocks(title="Travel Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🌍 AI Travel Assistant
        Welcome to your personal travel planner! I can help you:
        - Plan your trip itinerary
        - Provide travel recommendations
        - Answer questions about destinations
        
        Start by telling me about your travel plans!
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    value=[]
                )
                msg = gr.Textbox(
                    label="Type your message here...",
                    placeholder="e.g., I want to plan a trip to Japan for 7 days",
                    lines=2
                )
                
                with gr.Row():
                    submit = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear Conversation")
            
            with gr.Column(scale=1):
                preferences_md = gr.Markdown("""
                ### Current Travel Preferences
                - Destination: Not set
                - Duration: Not set
                - Budget: Not set
                - Interests: None
                - Travel Style: Not set
                """)
                generate_btn = gr.Button("Generate Itinerary", variant="secondary")
                itinerary_output = gr.Textbox(
                    label="Generated Itinerary",
                    lines=10,
                    interactive=False
                )
        
        # Event handlers
        msg.submit(
            process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        ).then(
            lambda: "",
            None,
            msg
        ).then(
            update_preferences_display,
            outputs=[preferences_md]
        )
        
        submit.click(
            process_message,
            inputs=[msg, chatbot],
            outputs=[chatbot]
        ).then(
            lambda: "",
            None,
            msg
        ).then(
            update_preferences_display,
            outputs=[preferences_md]
        )
        
        clear.click(
            clear_conversation,
            outputs=[chatbot, preferences_md]
        )
        
        generate_btn.click(
            generate_travel_itinerary,
            outputs=[itinerary_output]
        )

    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(
        server_name="127.0.0.1",
        share=True
    ) 