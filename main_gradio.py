# Simple Gradio chatbot application that responds with random text messages

import gradio as gr
import random

# Function to generate a random text response
def text_response(message):
    """Generate a random text response to the user's message."""
    responses = [
        "I understand your message: '{}'",
        "Thanks for sharing: '{}'",
        "Interesting point about: '{}'",
        "I'm processing your request about: '{}'",
        "Let me think about what you said: '{}'",
    ]
    return random.choice(responses).format(message)

# Main function to process messages
def process_message(message, history):
    """Process the user's message and return a text response."""
    return text_response(message)

# Setup the Gradio interface
with gr.Blocks() as demo:
    # Header section
    gr.Markdown("# Simple Chatbot Demo")
    gr.Markdown("Type a message to get a random response.")
    
    # Chat components
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="Type your message")
    clear = gr.Button("Clear")
    
    # Response handling function
    def respond(message, chat_history):
        """Add the user message and bot response to the chat history."""
        if not message:
            return "", chat_history
        
        # Get text response
        response = process_message(message, chat_history)
        
        # Add to chat history
        chat_history.append((message, response))
        
        return "", chat_history
    
    # Connect UI components to functions
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch()
