import os
import time
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "ai-tutor" 

# Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if index exists, if not, create it
existing_indexes = [index.name for index in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    print(f"Index '{INDEX_NAME}' not found. Creating it...")
    try:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384, # Match embedding model dimensions
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)

        print(f"Index '{INDEX_NAME}' created successfully!")
    except Exception as e:
        print(f"Error creating index: {e}")
        print("Please create the index 'ai-tutor' manually in the Pinecone console with dimension 384.")

# Connect to the index
index = pc.Index(INDEX_NAME)

# Initialize Embedding Model
embed_model = SentenceTransformer('all-MiniLM-L6-v2') 

def process_pdf(file_path: str, namespace: str):
    """
    Reads PDF, chunks text, creates embeddings, uploads to Pinecone.
    """
    # Extract Text
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Chunk Text
    chunk_size = 500
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Generate Embeddings
    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = embed_model.encode(chunk).tolist()
        vectors.append({
            "id": f"chunk_{i}",
            "values": embedding,
            "metadata": {"text": chunk}
        })
    
    # Upsert to Pinecone
    index.upsert(vectors=vectors, namespace=namespace)
    
    return len(chunks)

def query_rag(query: str, namespace: str):
    """
    Embeds query, searches Pinecone, returns context text.
    """
    # Embed Query
    query_emb = embed_model.encode(query).tolist()
    
    # Search Pinecone
    results = index.query(
        namespace=namespace,
        vector=query_emb,
        top_k=3,
        include_metadata=True
    )
    
    # Extract Text Context
    context_text = "\n".join([match['metadata']['text'] for match in results['matches']])
    return context_text