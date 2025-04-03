import gradio as gr
import os
from dotenv import load_dotenv
from app.models.llm import LLMHandler
from app.utils.prompts import generate_system_prompt

# Load environment variables
load_dotenv()

# Initialize the LLM handler
llm_handler = LLMHandler()

# Store conversation history
class ConversationState:
    def __init__(self):
        self.history = []
        self.current_preferences = {
            "destination": None,
            "duration": None,
            "budget": None,
            "interests": [],
            "travel_style": None
        }

state = ConversationState()

def update_preferences_display():
    prefs = state.current_preferences
    return f"""
    ### Current Travel Preferences
    - Destination: {prefs['destination'] or 'Not set'}
    - Duration: {f"{prefs['duration']} days" if prefs['duration'] else 'Not set'}
    - Budget: {f"${prefs['budget']}" if prefs['budget'] else 'Not set'}
    - Interests: {', '.join(prefs['interests']) if prefs['interests'] else 'None'}
    - Travel Style: {prefs['travel_style'] or 'Not set'}
    """

def process_message(message, history):
    try:
        # Convert Gradio history format to LLMHandler format
        context = [
            {"user": msg["content"] for msg in dialog if msg["role"] == "user"}
            for dialog in (history if history else [])
        ]
        
        # Generate response using LLM
        response = llm_handler.generate_response(message, context)
        
        # Update preferences
        update_preferences(message)
        
        # Return the history in the new format Gradio expects
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return history
    except Exception as e:
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"Error: {str(e)}"})
        return history

def update_preferences(message):
    # Simple preference extraction logic
    message = message.lower()
    
    # Extract destination
    if "to " in message and " for " in message:
        destination = message.split("to ")[1].split(" for ")[0]
        state.current_preferences["destination"] = destination
    
    # Extract duration
    if " for " in message and " days" in message:
        try:
            duration = int(message.split(" for ")[1].split(" days")[0])
            state.current_preferences["duration"] = duration
        except ValueError:
            pass
    
    # Extract budget
    if "$" in message:
        try:
            budget = float(message.split("$")[1].split()[0])
            state.current_preferences["budget"] = budget
        except ValueError:
            pass
    
    # Extract interests
    interests = ["culture", "food", "adventure", "relaxation", "shopping", "history", "nature"]
    found_interests = [i for i in interests if i in message]
    if found_interests:
        state.current_preferences["interests"] = found_interests
    
    # Extract travel style
    styles = ["luxury", "budget", "mid-range"]
    for style in styles:
        if style in message:
            state.current_preferences["travel_style"] = style
            break

def generate_travel_itinerary():
    if not state.current_preferences["destination"]:
        return "Please provide a destination first."
    
    try:
        prompt = generate_system_prompt(state.current_preferences)
        itinerary = llm_handler.generate_itinerary(prompt)
        return itinerary
    except Exception as e:
        return f"Error generating itinerary: {str(e)}"

def clear_conversation():
    state.history = []
    state.current_preferences = {
        "destination": None,
        "duration": None,
        "budget": None,
        "interests": [],
        "travel_style": None
    }
    return [], update_preferences_display()

# Create the Gradio interface
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
                value=[],
                type="messages"
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

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=True
    ) 