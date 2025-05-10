## WORK IN PROGRESS

import gradio as gr
import numpy as np
import tempfile
import random
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# Function to respond with text
def text_response(message):
    responses = [
        "I understand your message: '{}'",
        "Thanks for sharing: '{}'",
        "Interesting point about: '{}'",
        "I'm processing your request about: '{}'",
        "Let me think about what you said: '{}'",
    ]
    return random.choice(responses).format(message)

# Function to respond with an image
def image_response(message):
    # Create a simple image with the message text
    img = Image.new('RGB', (400, 200), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Try to load a font, use default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()
    
    d.text((10, 10), f"Image response to: {message}", fill=(255, 255, 255), font=font)
    d.text((10, 50), f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
           fill=(255, 255, 255), font=font)
    
    return img

# Function to provide a document
def document_response(message):
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp:
        temp.write(f"Document response to: {message}\n".encode())
        temp.write(f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n".encode())
        temp.write(f"This is a sample document generated in response to your query.\n".encode())
        temp.write(f"Your message was: {message}\n".encode())
        for i in range(5):
            temp.write(f"Sample content line {i+1}\n".encode())
        
        file_path = temp.name
    
    return file_path

# Main function to process messages and generate appropriate responses
def process_message(message, history):
    # Determine response type based on keywords or random selection
    if "image" in message.lower():
        img = image_response(message)
        return img
    elif "document" in message.lower() or "file" in message.lower():
        doc_path = document_response(message)
        return doc_path
    else:
        text = text_response(message)
        return text

# Setup the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Dynamic Response Demo")
    gr.Markdown("Type a message to get a response. Include 'image' to get an image response or 'document'/'file' to get a document.")
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="Type your message")
    clear = gr.Button("Clear")
    
    def respond(message, chat_history):
        if not message:
            return "", chat_history
        
        # Get response based on message content
        response = process_message(message, chat_history)
        
        # Handle different response types
        if isinstance(response, Image.Image):
            # For image responses
            chat_history.append((message, (response, None)))
        elif isinstance(response, str) and os.path.exists(response) and response.endswith('.txt'):
            # For document responses
            with open(response, 'r') as f:
                file_content = f.read()
            os.unlink(response)  # Delete the temporary file
            chat_history.append((message, f"Document response: [Download not available in this demo]\n\nPreview:\n{file_content[:200]}..."))
        else:
            # For text responses
            chat_history.append((message, response))
        
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch()