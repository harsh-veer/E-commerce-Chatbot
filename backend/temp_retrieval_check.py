import asyncio
from app.database.client import db
from app.rag.pipeline import retrieve_answer, load_faiss_index

async def main():
    count = await db.products.count_documents({})
    print('product_count=', count)
    idx, meta = load_faiss_index()
    print('faiss_loaded=', idx is not None, 'meta_count=', len(meta) if meta else 0)
    answer = await retrieve_answer('I want to buy a mobile phone')
    print('answer=', answer)
    db.client.close()

asyncio.run(main())
