# Simple Gradio chatbot application that uses Gemma 3 1B for responses
import gradio as gr
from model import gemma_response
from fetch_email import fetch_email

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup
import urllib.parse

def bing_search(query, max_results=10):
    params = {"q": query, "count": max_results}
    resp = requests.get("https://www.bing.com/search", params=params)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for h2 in soup.select("li.b_algo h2"):
        a = h2.find("a")
        if a and a["href"]:
            title = a.get_text()
            url = a["href"]
            links.append((title, url))
    return links



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

        print()
        print(('-----------------Actual responce-------------------'))
        print(bot_response)
        print('----------------------------------------------------')


        if "R€@d_€m@il" in bot_response:
            email_response = fetch_email(5) 
            email_response = "Give me a detailed Summarize this emails for me and print it: " + email_response
            bot_response,_ = gemma_response(email_response, instruction = instructions_str, history=formatted_history)
        
        if 'SEARCH' in bot_response:
            search_query = bot_response.split(', ')[1].strip()
            if '?' in search_query:
                search_query = search_query.split('?')[0].strip()

            print("search_query", search_query)
            search_results = str(bing_search(search_query))
            print("search_results", search_results)
            sumarized_requested = "This is a result of a search result regarding " + search_query+ ". tell me what you find in these results in few sentences and give a complete responce: " + search_results
            bot_response, _ = gemma_response(sumarized_requested, instruction = instructions_str, history=formatted_history)
        
        
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
