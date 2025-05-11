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
    
    # Use Chatbot component to display the conversation
    chatbot = gr.Chatbot(label="Conversation")
    msg = gr.Textbox(label="Type your message")
    clear = gr.Button("Clear")
    
    # State to maintain conversation history for the model
    conversation_history = gr.State([])

    def respond(message, history, chat_history):
        """Get the model response and update the chatbot display"""
        if not message:
            return "", history, chat_history
        
        # Format chat history for the model
        formatted_history = []
        for i in range(0, len(history), 2):
            if i+1 < len(history):
                formatted_history.append((history[i], history[i+1]))
        
        # Get response from the model
        bot_response, _ = gemma_response(message, instruction = instructions_str, history=formatted_history)
        
        # Update internal history for the model
        history = history + [message, bot_response]
        
        # Update chat display
        chat_history = chat_history + [[message, bot_response]]
        
        return "", history, chat_history


    # Connect UI components to functions
    msg.submit(respond, [msg, conversation_history, chatbot], [msg, conversation_history, chatbot], queue=True)
    clear.click(lambda: ("", [], []), None, [msg, conversation_history, chatbot], queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch()
