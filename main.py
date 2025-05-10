# Simple Gradio chatbot application that uses Gemma 3 1B for responses
import gradio as gr
from model import gemma_response



with open("instructions.txt", "r", encoding="utf-8") as file:
    instructions_str = file.read()

print(instructions_str)

# Setup the Gradio interface
with gr.Blocks() as demo:
    # Header section
    gr.Markdown("# Gemma 3 1B Chatbot")
    gr.Markdown("Type a message to get a response from Gemma 3 1B.")
    
    # Use a regular Textbox for display instead of Chatbot
    response_area = gr.Textbox(label="AI Response", lines=8, interactive=False)
    msg = gr.Textbox(label="Type your message")
    clear = gr.Button("Clear")
    
    # State to maintain conversation history
    conversation_history = gr.State([])
    
    def respond(message, history):
        """Get the model response while maintaining history internally"""
        if not message:
            return "", history
        
        # Format chat history for the model
        formatted_history = []
        for i in range(0, len(history), 2):
            if i+1 < len(history):
                formatted_history.append((history[i], history[i+1]))
        
        # Get response from the model
        bot_response, _ = gemma_response(message, instruction = instructions_str, history=formatted_history)
        
        # Update internal history
        history.append(message)
        history.append(bot_response)
        
        # Only return the latest response to display
        return "", bot_response, history

    # Connect UI components to functions
    msg.submit(respond, [msg, conversation_history], [msg, response_area, conversation_history], queue=True)
    clear.click(lambda: ["", []], None, [response_area, conversation_history], queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch()
