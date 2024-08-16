from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from psycopg2.extras import RealDictCursor
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import io
import os
import numpy as np

from models import Tenant, Query
from database import get_db_connection


app = FastAPI()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

@app.post("/tenants")
async def create_tenant(tenant: Tenant, conn = Depends(get_db)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("INSERT INTO tenants (name) VALUES (%s) RETURNING id, name", (tenant.name,))
            new_tenant = cur.fetchone()
            conn.commit()
        return new_tenant
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/tenants")
async def get_tenants(conn = Depends(get_db)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM tenants")
            tenants = cur.fetchall()
        return tenants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: int, conn = Depends(get_db)):
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tenants WHERE id = %s RETURNING id", (tenant_id,))
            deleted = cur.fetchone()
            conn.commit()
        if deleted:
            return {"message": f"Tenant with ID {tenant_id} deleted successfully"}
        raise HTTPException(status_code=404, detail="Tenant not found")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/upload/{tenant_id}")
async def upload_file(tenant_id: int, file: UploadFile = File(...), conn = Depends(get_db)):
    try:
        # Read the PDF file
        content = await file.read()
        
        # Use PyPDFLoader to load the PDF content
        pdf_file = io.BytesIO(content)
        loader = PyPDFLoader(pdf_file)
        pages = loader.load()
        
        # Initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Split the document into chunks
        chunks = text_splitter.split_documents(pages)
        
        # Generate embedding using Gemini
        embedding_model = genai.GenerativeModel('text-embedding-004')
        
        # Store chunks and their embeddings in the database
        with conn.cursor() as cur:
            for chunk in chunks:
                chunk_text = chunk.page_content
                embedding = embedding_model.embed_content(content=chunk_text)
                
                cur.execute(
                    "INSERT INTO knowledge_base (tenant_id, filename, chunk_content, embedding) VALUES (%s, %s, %s, %s)",
                    (tenant_id, file.filename, chunk_text, embedding.values)
                )
            
            conn.commit()
        
        return {"message": f"File uploaded and processed successfully. {len(chunks)} chunks created and stored."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/query/{tenant_id}")
async def query_knowledge_base(tenant_id: int, query: Query, conn = Depends(get_db)):
    try:
        # Generate embedding for the query
        embedding_model = genai.GenerativeModel('text-embedding-004')
        query_embedding = embedding_model.embed_content(content=query.text).values

        # Convert the embedding to a numpy array and then to a list
        query_embedding_list = np.array(query_embedding).tolist()

        # Perform the similarity search
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT chunk_content, filename, 
                       1 - (embedding <=> %s) AS cosine_similarity
                FROM knowledge_base
                WHERE tenant_id = %s
                ORDER BY cosine_similarity DESC
                LIMIT %s
            """, (query_embedding_list, tenant_id, query.k))
            
            results = cur.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No relevant results found")

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)