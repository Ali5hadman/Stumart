import os
import datetime
from pathlib import Path
from transformers import AutoTokenizer, BitsAndBytesConfig, Gemma3ForCausalLM
import torch
import torch

# variables
os.environ["HF_HOME"] = "C:\\Users\\gabri\\Desktop\\Gabriele\\Stumart\\transformers_cache"
model_id = "./gemma-3-1b-it"
device = "cuda" if torch.cuda.is_available() else "cpu"
# Only use quantization if CUDA is available
quantization_config = BitsAndBytesConfig(load_in_8bit=True) if device == "cuda" else None

# logs
txt_log = True  # Toggle to enable/disable logging
log_dir = Path("chat_logs")  # Directory for storing logs
if txt_log:
    log_dir.mkdir(exist_ok=True)
try:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # Use different loading approaches based on device availability
    if device == "cuda":
        model = Gemma3ForCausalLM.from_pretrained(
            model_id, quantization_config=quantization_config
        ).eval()
    else:
        # For CPU, load with reduced precision or smaller model settings
        model = Gemma3ForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.float32, low_cpu_mem_usage=True
        ).eval()
    model_loaded = True
    print(f"Model loaded successfully on {device}")
except Exception as e:
    print(f"Errore nel caricamento del modello: {e}")
    model_loaded = False
    model_loaded = False

# Function to generate a complete response using Gemma 3 1B that expects a prompt, an instruction and a model
def gemma_response(prompt, instruction=None, history=None):
    """
    Generate a response using Gemma 3 1B model.
    
    Args:
        prompt (str): The user's current input
        instruction (str, optional): System instruction for the model
        history (list, optional): List of previous conversation turns as (user_msg, assistant_msg) tuples
    """
    global model, tokenizer, model_loaded
    
    if not model_loaded:
        return "Model is not loaded properly. Please check the initialization.", []
    
    # Initialize history if None
    if history is None:
        history = []
    
    # Create a conversation (list of messages)
    conversation = []
    
    # Add system message with instruction
    system_msg = instruction if instruction else "You are a helpful assistant, reply shortly and concisely."
    conversation.append({
        "role": "system",
        "content": [{"type": "text", "text": system_msg}]
    })
    
    # Add conversation history
    for user_msg, assistant_msg in history:
        conversation.append({
            "role": "user",
            "content": [{"type": "text", "text": user_msg}]
        })
        conversation.append({
            "role": "assistant",
            "content": [{"type": "text", "text": assistant_msg}]
        })
    
    # Add current user message
    conversation.append({
        "role": "user",
        "content": [{"type": "text", "text": prompt}]
    })
    
    # Format as expected by the tokenizer
    messages = conversation
    
    # Get input tokens length to track where new content begins
    chat_template = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False,
        return_tensors=None
    )
    input_tokens_len = len(tokenizer.encode(chat_template))
    
    # Tokenize the input
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    
    # Convert only the tensor values to bfloat16 if we're using CUDA
    if device == "cuda":
        inputs = {k: v.to(torch.bfloat16) if torch.is_tensor(v) else v for k, v in inputs.items()}
    
    # Generate response
    with torch.inference_mode():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=256,
            do_sample=True,
            temperature=0.3
        )
    
    # Extract only the newly generated tokens (the model's response)
    output_tokens = outputs[0][input_tokens_len:]
    model_response = tokenizer.decode(output_tokens, skip_special_tokens=True).strip()
    
    # Log conversation if enabled
    if txt_log:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"chat_log_{timestamp}.txt"
        
        log_dir.mkdir(exist_ok=True, parents=True)
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {model_id}\n\n")
            f.write(f"System: {system_msg}\n\n")
            
            if history:
                f.write("=== Conversation History ===\n")
                for user_msg, assistant_msg in history:
                    f.write(f"User: {user_msg}\n")
                    f.write(f"Assistant: {assistant_msg}\n\n")
                f.write("=== Current Exchange ===\n")
            
            f.write(f"User: {prompt}\n")
            f.write(f"Assistant: {model_response}\n")
    
    # Add the current exchange to history and return
    updated_history = history + [(prompt, model_response)]
    return model_response, updated_history

if __name__ == "__main__":
    # Test the model with a simple prompt
    test_prompt = "Ciao, come stai?"
    response, _ = gemma_response(test_prompt)
    print(f"Response: {response}")
