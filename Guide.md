# Development Plan: AI-Powered Python Application with Gradio Interface

## Project Goal:

To create a Python application featuring a Gradio web interface where users can submit text requests. These requests are processed by a local Large Language Model (LLM) augmented by a Retrieval Augmented Generation (RAG) system accessing a user-specific vector database. The application will be capable of diverse outputs (audio, images, files, text) and actions (online search, calendar integration, email replies, Outlook/Teams data retrieval).

---

## Phase 1: Core Local RAG System & Basic Interface

* **Objective:** Get a basic version of the local LLM answering questions based on user-provided documents.

  1. **Step 1: Setup Local LLM Environment**

     * **LLM Selection & Installation:**
       * Choose an initial LLM (e.g., Gemma, Llama 3, DeepSeek Coder). Consider model size vs. performance and hardware.
       * Download model weights.
       * Set up Python environment: `transformers`, `torch`, `accelerate`, `bitsandbytes` (for quantization if needed).
     * **Basic LLM Interaction Script:**
       * Load the chosen LLM.
       * Implement a function: text prompt in -> LLM text response out. Test thoroughly.
  2. **Step 2: Initial Gradio Web Interface**

     * **Library:** `gradio`
     * **Functionality:**
       * Interface: `gr.Textbox()` for user query, `gr.Textbox()` for LLM output.
       * Connect to the LLM script from Step 1.
  3. **Step 3: Vector Database & Basic RAG Implementation**

     * **A. Vector Database Selection & Setup:**
       * **Choice (Local):** `ChromaDB`, `FAISS`, or `LanceDB`. Nice to have: file paths to let the user double check.
       * **Installation:** `pip install chromadb` / `faiss-cpu` / `faiss-gpu` / `lancedb`.
     * **B. Embedding Model:**
       * **Choice:** Sentence Transformers (e.g., `all-MiniLM-L6-v2`, `BAAI/bge-small-en-v1.5`).
       * **Installation:** `pip install sentence-transformers`.
     * **C. Document Loading & Preprocessing (Initial Focus: Text Files):**
       * **File Input:** Allow user to specify a directory of `.txt` files (or hardcode for testing).
       * **Document Loaders:** Use libraries like `langchain-community` document loaders (`TextLoader`, `PyPDFLoader` later) or custom loaders.
       * **Text Chunking:**
         * **Why:** LLM context limits, effective retrieval on smaller chunks.
         * **Strategy:** `RecursiveCharacterTextSplitter` (Langchain) or custom (fixed size with overlap).
         * **Metadata:** Store content and metadata (source filename, chunk number) for each chunk.
     * **D. Vectorization & Storage (Ingestion Pipeline):**
       * Script/function:
         1. Load documents.
         2. Chunk documents.
         3. Generate embeddings for each chunk (using the chosen sentence transformer).
         4. Store chunk text, embedding, and metadata (filename) in the vector database.
     * **E. Retrieval Mechanism:**
       * On user query (from Gradio):
         1. Generate embedding for the user query (same sentence transformer).
         2. Perform similarity search (e.g., cosine similarity) in vector DB for top-K relevant chunks.
     * **F. Context Augmentation & LLM Generation:**
       * Concatenate retrieved chunk content with the original user query to form an "augmented prompt."
         ```
         Context from documents:
         [Chunk 1 text from doc_A.txt]
         [Chunk 2 text from doc_B.txt]
         ---
         User Query: [Original user query]
         ---
         Answer:
         ```
       * Feed augmented prompt to your local LLM.
     * **G. Update Gradio Interface:**
       * Display context-aware LLM response.
       * Display information sources (e.g., filenames of documents from which chunks were retrieved).

---

## Phase 2: Enhancing RAG, User Interaction, and Output

* **Objective:** Make the RAG system more robust, improve source linking, handle missing information, and start diversifying output.

  4. **Step 4: Improved Source Linking & File Access**

     * **Functionality:**
       * Store/retrieve precise metadata (page numbers for PDFs later).
       * Gradio output: clickable links to source files (serve files locally or use `file://` URLs cautiously).
     * **LLM Instruction:** Prompt LLM (system prompt) to cite sources from provided context.
  5. **Step 5: Handling Insufficient Information & Requesting Additional Files**

     * **Logic for LLM:**
       * Recognize insufficient retrieved context (prompt engineering or confidence scores).
       * Generate response asking user for more specific files if information is missing.
     * **Gradio Interface Update:**
       * Add `gr.File()` for file uploads.
       * Process uploaded files (chunk, embed, add to vector DB) on-the-fly. Re-run RAG.
     * **Fallback:** If user can't provide files, LLM answers with limitations or states it cannot answer (else search online).
  6. **Step 6: Basic Multi-Modal Output - Text & Files**

     * **Text Output:** Implemented.
     * **File Output:**
       * If a query requests a specific file, allow LLM to identify this (eg: relevant files location).
       * Gradio: present file as a downloadable link (`gr.File()` output component).

---

## Phase 3: Expanding Capabilities - Online Search and Basic Actions

* **Objective:** Allow LLM to fetch external information and perform simple, predefined actions.

  7. **Step 7: Online Search Integration (Tool Use - Initial)**

     * **Tool Definition:** `search_online` tool.
     * **API Choice:** Tavily AI, Serper API, Google Custom Search JSON API.
     * **LLM Triggering:**
       * Prompt LLM to decide when to use the tool and with what query (e.g., structured output like JSON for tool calls, or use function-calling models).
       * Python code parses LLM output, calls search API.
     * **Execution Flow:**
       1. User query -> LLM processes -> LLM requests search.
       2. App executes search -> Search results fed back to LLM as context.
       3. LLM generates final answer.
       4. IF the request generate a PDF (eg: when using the Deep Search mode on ChatGPT or Gemini) save it in the Vector DB
     * **Gradio Update:** Indicate when search results are used and saved.
  8. **Step 8: Basic Action - Calendar Event Insertion (Example)**

     * **Scope:** One simple, well-defined action (e.g., create calendar event).
     * **Tool Definition:** `Calendar` (parameters: `summary`, `start_datetime`, `end_datetime`, `description`).
     * **Calendar API:**
       * Google Calendar/Outlook (OAuth2, e.g., `google-api-python-client`, `O365`/MS Graph API) or local `.ics` file (`ics.py`).
     * **LLM Triggering & Parameter Extraction:** LLM identifies intent and extracts parameters from natural language.
     * **Execution & Confirmation:**
       1. LLM outputs tool request with parameters.
       2. Python code executes calendar action.
       3. Report success/failure to user via LLM/Gradio.
       4. **Highly Recommended:** LLM confirms details with user *before* action execution.

---

## Phase 4: Advanced Actions, Agentic Behavior, and Output Diversification

* **Objective:** Integrate with complex applications, enable more autonomous actions, support richer output.

  9. **Step 9: Deeper Application Integration (Outlook/Teams Data Retrieval)**

     * **Authentication:** Robust OAuth2 for Microsoft Graph API. Secure token storage.
     * **Scope for Outlook:** `search_emails` (sender, subject, date), `get_contact_details`.
     * **Scope for Teams:** `search_teams_messages` (keywords, channel, user, date).
     * **Data Handling:** Summarize/process retrieved data (emails, messages) by LLM. Mind privacy and volume.
     * **Agent Framework:** Consider a formal agent/tool-use framework (Langchain, LlamaIndex, or custom) for managing multiple tools.
  10. **Step 10: Autonomous Email Responses (with Safeguards)**

      * **High Risk:** Careful implementation.
      * **LLM Intent & Drafting:**
        1. Reliably identify when reply is needed.
        2. Understand context of email to be replied to.
        3. Draft appropriate reply.
      * **Safeguard - User Confirmation:**
        * **Always** show drafted email in Gradio.
        * Require explicit user confirmation (button) before sending.
        * Allow user to edit draft.
      * **Sending Mechanism:** Microsoft Graph API.
  11. **Step 11: Richer Output Modalities - Audio & Images**

      * **Audio Output (Text-to-Speech):**
        * **Libraries:** `pyttsx3` (offline), `gTTS` (online), or cloud TTS APIs (OpenAI, Google, Azure).
        * **Gradio Integration:** `gr.Audio()` output. Button "Read Aloud" or auto-play.
      * **Image Output:**
        * **Use Case 1 (Retrieved):** Display images from user files via `gr.Image()`.
        * **Use Case 2 (Generated - Advanced):** Integrate image generation model (e.g., Stable Diffusion via `diffusers` or API). LLM describes image to generate.

---

## General Considerations Throughout Development:

* **System Prompt Engineering:** Crucial for guiding LLM behavior, response style, tool usage, context use. Iterate continuously.
* **Error Handling:** Robust handling for API calls, file ops, LLM issues. Clear user feedback.
* **Security:**
  * API Keys: Store securely (env vars, `.env` files, secrets managers). No hardcoding.
  * File Access: Mind application permissions.
* **Modularity:** Keep components (LLM interface, RAG, Gradio UI, tools) modular.
* **Logging:** Comprehensive logging for debugging, LLM reasoning, tool calls.
* **User Experience (UX):** Focus on intuitive interaction.
* **Configuration:** Easy configuration for models, paths, API keys.

---
