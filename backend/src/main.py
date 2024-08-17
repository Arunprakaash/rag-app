from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from psycopg2.extras import RealDictCursor
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from io import BytesIO
import os

from consts import EMBEDDING_MODEL, LLM
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
async def create_tenant(tenant: Tenant, conn=Depends(get_db)):
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
async def get_tenants(conn=Depends(get_db)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM tenants")
            tenants = cur.fetchall()
        return tenants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: int, conn=Depends(get_db)):
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
async def upload_file(tenant_id: int, file: UploadFile = File(...), conn=Depends(get_db)):
    try:
        content = await file.read()
        pdf_file = BytesIO(content)
        pdf_reader = PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
        chunks = text_splitter.split_text(text)

        # Prepare batch insert
        insert_data = []
        for chunk in chunks:
            embedding = genai.embed_content(model=EMBEDDING_MODEL, content=chunk)['embedding']
            insert_data.append((tenant_id, file.filename, chunk, embedding))

        # Batch insert into the database
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO knowledge_base (tenant_id, filename, chunk_content, embedding) VALUES (%s, %s, %s, %s)",
                insert_data
            )
            conn.commit()

        return {"message": f"File uploaded and processed successfully. {len(chunks)} chunks created and stored."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/query/{tenant_id}")
async def query_knowledge_base(tenant_id: int, query: Query, conn=Depends(get_db)):
    try:
        # Generate embedding for the query
        # embedding_model = genai.get_model(EMBEDDING_MODEL)
        query_embedding = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query.text
        )['embedding']

        # Convert the embedding to a numpy array and then to a list
        # query_embedding_list = np.array(query_embedding).tolist()

        # Perform the similarity search
        with conn.cursor() as cur:
            cur.execute(f"""
                        SELECT chunk_content, filename, 1 - (embedding <=> '{query_embedding}') AS cosine_similarity
                        FROM knowledge_base
                        WHERE tenant_id = '{tenant_id}'
                        ORDER BY cosine_similarity desc
                        LIMIT {query.k}
                        """)

            results = cur.fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No relevant results found")

        # Extract relevant chunks from the results
        relevant_chunks = "\n\n".join([result[0] for result in results])

        llm = genai.GenerativeModel(
            model_name=LLM,
            safety_settings={
                'HATE': 'BLOCK_NONE',
                'HARASSMENT': 'BLOCK_NONE',
                'SEXUAL': 'BLOCK_NONE',
                'DANGEROUS': 'BLOCK_NONE'
            }
        )

        # Use the LLM to generate a response based on the retrieved chunks
        llm_response = llm.generate_content(
            f"Based on the following information: {relevant_chunks}, answer the question: {query.text}",
        ).text

        return {"results": results, "llm_response": llm_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
