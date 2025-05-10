# Simple Gradio chatbot application that uses Gemma 3 1B for responses

import os
import datetime
from pathlib import Path
import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Imposta la variabile d'ambiente prima di importare transformers
os.environ["HF_HOME"] = "C:\\Users\\gabri\\Desktop\\Gabriele\\Stumart\\transformers_cache"

# Logging configuration
txt_log = True  # Toggle to enable/disable logging
log_dir = Path("chat_logs")  # Directory for storing logs

# Ensure log directory exists
if txt_log:
    log_dir.mkdir(exist_ok=True)

# Load Gemma 3 1B model and tokenizer
model_name = "./gemma-3-1b-it"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
    model_loaded = True
except Exception as e:
    print(f"Errore nel caricamento del modello: {e}")
    model_loaded = False

# Function to generate a complete response using Gemma 3 1B
def gemma_response(message, stop_token="<STOP>"):
    """Generate a complete response using Gemma 3 1B model."""
    if not model_loaded:
        return "Modello non caricato correttamente. Controlla i log per dettagli."
    
    # Prepara il prompt
    prompt = f"""User said: {message}
    
    Answer to the question above in a helpful and short way. When you are done, add '{stop_token}' at the end of your answer.

    Assistant : """
    
    # Tokenizza l'input
    input_ids = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Genera risposta completa
    output = model.generate(
        **input_ids,
        max_new_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        return_dict_in_generate=True,
        output_scores=False,
    )
    
    # Decodifica la risposta completa
    generated_tokens = output.sequences[0][len(input_ids.input_ids[0]):]
    decoded_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    # Rimuovi il testo dopo il token di stop se presente
    if stop_token in decoded_text:
        decoded_text = decoded_text.split(stop_token)[0]
    
    return decoded_text

def log_chat_exchange(user_message, bot_response):
    """Log a chat exchange to a file."""
    if not txt_log:
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"chat_{timestamp}.txt"
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"User: {user_message}\n\n")
        f.write(f"Assistant: {bot_response}\n")

# Setup the Gradio interface
with gr.Blocks() as demo:
    # Header section
    gr.Markdown("# Gemma 3 1B Chatbot")
    gr.Markdown("Type a message to get a response from Gemma 3 1B.")
    
    chatbot = gr.Chatbot(height=400, type='messages')
    msg = gr.Textbox(label="Type your message")
    clear = gr.Button("Clear")
    
    # Update the respond function to use the new format
    def respond(message, chat_history):
        """Add the user message and bot response to the chat history."""
        if not message:
            return "", chat_history
        
        # Get complete response
        bot_response = gemma_response(message)
        
        # Log the interaction
        if txt_log:
            log_chat_exchange(message, bot_response)
        
        # Add to chat history using the messages format
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_response})
        
        return "", chat_history

    # Connect UI components to functions
    msg.submit(respond, [msg, chatbot], [msg, chatbot], queue=True)
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch()
