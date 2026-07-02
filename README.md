MSP Corp IT Ticket Automation Engine

An intelligent, AI-powered IT Support Ticket Automation Engine designed to streamline enterprise helpdesk workflows. By utilizing a Retrieval-Augmented Generation (RAG) architecture, this application surfaces contextual resolutions from internal data documentation to dramatically reduce ticket resolution times.


🚀 Key Features

* Intelligent Document Retrieval: Semantic search using a local FAISS vector store to locate relevant IT resolution history.
* Contextual Answer Generation  : Powered by LangChain and OpenAI LLMs to generate precise, step-by-step resolution steps for IT agents.
* Robust Backend Infrastructure : Fast, asynchronous REST APIs built with FastAPI to manage incoming query payloads.
* Structured Data Handling      : Automatically ingests and parses historical IT ticket datasets (`.csv`) for knowledge embedding.



📂 Project Architecture


LLM_RAG_TICKET/
│
├── api/                # FastAPI application backend and routing
│   ├── __init__.py
│   └── app.py
│
├── data/               # Source knowledge base datasets
│   └── IT_Service_Tickets.csv
│
├── embeddings/         # Local vector database indexing
│   └── faiss_index/
│
├── rag/                # Core LLM engineering logic
│   ├── __init__.py
│   ├── generator.py    # Text generation workflows
│   ├── prompt.py       # Tailored system prompts
│   └── retriever.py    # FAISS semantic search wrappers
│
├── utils/              # Data parsing and text preprocessing
│   ├── __init__.py
│   └── preprocess.py
│
├── main.py             # Server initialization gateway
└── .gitignore          # Environment security rules



🛠️ Tech Stack


* Language       : Python
* LLM Framework  : LangChain
* Vector Store   : FAISS (Facebook AI Similarity Search)
* Embedding Model: OpenAI Embeddings
* API Framework  : FastAPI & Uvicorn



🔬 Extended Technical Description

   This automation engine implements a production-grade, modular Retrieval-Augmented Generation (RAG) architecture tailored specifically for managing                unstructured internal service desk documentation. 

  
   Deep Dive: Architectural Workflow


+-------------------+     +---------------------+     +----------------------+
|  Incoming Ticket  | --> | Semantic Retrieval  | --> | Prompt Augmentation  |
| (Customer Issue)  |     |  (FAISS Indexing)   |     | (Context Injection)  |
+-------------------+     +---------------------+     +----------------------+
                                                                 |
                                                                 v
+-------------------+                                 +----------------------+
| Automated Ticket  | <------------------------------ |     LLM Inference    |
|   Resolution      |                                 |   (OpenAI GPT-4)     |
+-------------------+                                 +----------------------+



1. Document Ingestion & Chunking Optimization
  
   Historical service tickets stored in data/IT_Service_Tickets.csv undergo structural parsing via the pipeline's preprocessing utility (utils/preprocess.py). To    maintain semantic continuity while staying within the LLM's optimal context window context limits, documents are chunked using recursive character text           splitting with an intentional overlap margin. This mitigates boundary issues where vital troubleshooting context might otherwise be severed.

2. Vector Space Indexing (FAISS)The generated text chunks are mapped into high-dimensional vector space using OpenAI's embedding models. The mathematical vectors    are indexed locally inside embeddings/faiss_index/ using FAISS (Facebook AI Similarity Search). The index utilizes L2 Euclidean distance measurements to          execute rapid, low-latency semantic searches when querying text.
  
3. Contextual Retrieval & Prompt EngineeringWhen a new IT support ticket payload hits the FastAPI endpoint (api/app.py), the query is vectorized in real-time.       The rag/retriever.py module queries the local FAISS index to extract the top $K$ most semantically relevant historical resolution blocks.The core logic inside    rag/generator.py then acts as the orchestration layer:It extracts the text from the top-scoring vector matches.It injects this documentation as "ground truth"    context directly into a strictly isolated system prompt (rag/prompt.py).This prevents the model from hallucinating generic web advice, forcing it to generate     step-by-step resolution pathways grounded entirely in your company's actual historical IT datasets.



1. Installation

   Clone the repository and install the dependencies inside your environment:

   git clone [https://github.com/mukthaar917/LLM_RAG_TICKET.git](https://github.com/mukthaar917/LLM_RAG_TICKET.git)
   
   cd LLM_RAG_TICKET
   
   pip install -r requirements.txt
   
   

 3. Environment Setup

    Configure your API credentials safely in your local workspace:

    export OPENAI_API_KEY="your-api-key-here"
    


 5. Run the Automation Engine

    Launch the API server using Uvicorn:

    python main.py

    The server will initialize on `http://127.0.0.1:8000`. You can explore the interactive API documentation at `http://127.0.0.1:8000/docs`.
    



📤 How to Push the README to GitHub

   Open the terminal window and push it live with these final three commands :


      git add README.md
     
      git commit -m "Docs: Added professional project overview README"
     
      git push -u origin master

