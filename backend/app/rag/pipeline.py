import json
import logging
import os
import re
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.database.client import db
from app.rag.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

INDEX_DIR = "faiss_index"
INDEX_FILE = os.path.join(INDEX_DIR, "index.faiss")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.json")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        logger.info("Loading embedding model...")
        _embedding_model = SentenceTransformer(MODEL_NAME)

    return _embedding_model


def normalize_search_terms(text: str) -> set[str]:

    words = set(re.findall(r"\w+", text.lower()))

    normalized = set(words)

    synonyms = {
        "phone": "mobile",
        "phones": "mobile",
        "cellphone": "mobile",
        "smartphone": "mobile",
        "mobiles": "mobile",
        "tv": "television",
        "televisions": "television",
        "notebook": "laptop",
        "notebooks": "laptop",
        "earbud": "headphones",
        "earbuds": "headphones",
        "watch": "smartwatch",
        "gaming": "game",
        "shoe": "shoes",
    }

    for word in list(normalized):

        if word.endswith("s"):
            normalized.add(word[:-1])

        else:
            normalized.add(word + "s")

        if word in synonyms:
            normalized.add(synonyms[word])

    return normalized


def build_documents(products):

    docs = []

    for product in products:

        specs = "\n".join(
            f"{k}: {v}"
            for k, v in product["specifications"].items()
        )

        docs.append(
            {
                "id": str(product["_id"]),
                "name": product["name"],
                "brand": product["brand"],
                "category": product["category"],
                "content":
f"""
Product : {product['name']}
Brand : {product['brand']}
Category : {product['category']}
Price : ${product['price']}
Discount : {product['discount']}%
Rating : {product['rating']}
Stock : {product['stock']}

Description :
{product['description']}

Specifications

{specs}
"""
            }
        )

    return docs


def save_index(index, metadata):

    os.makedirs(INDEX_DIR, exist_ok=True)

    faiss.write_index(index, INDEX_FILE)

    with open(METADATA_FILE, "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=2)


def load_index():

    if not os.path.exists(INDEX_FILE):
        return None, None

    if not os.path.exists(METADATA_FILE):
        return None, None

    index = faiss.read_index(INDEX_FILE)

    with open(METADATA_FILE, encoding="utf8") as f:
        metadata = json.load(f)

    return index, metadata


async def build_faiss():

    logger.info("Building FAISS Index...")

    products = await db.products.find().to_list(1000)

    docs = build_documents(products)

    model = get_embedding_model()

    vectors = model.encode(
        [doc["content"] for doc in docs],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    vectors = np.asarray(vectors, dtype=np.float32)

    index = faiss.IndexFlatIP(vectors.shape[1])

    index.add(vectors)

    save_index(index, docs)

    logger.info("FAISS Index Created")
async def get_or_build_index():
    index, metadata = load_index()

    if index is not None:
        return index, metadata

    await build_faiss()

    return load_index()


def rank_products(question: str, products):

    keywords = normalize_search_terms(question)

    ranked = []

    for product in products:

        score = 0

        name = product.get("name", "").lower()
        brand = product.get("brand", "").lower()
        category = product.get("category", "").lower()
        description = product.get("description", "").lower()

        specs = " ".join(
            str(v).lower()
            for v in product.get("specifications", {}).values()
        )

        for word in keywords:

            if word in name:
                score += 10

            if word in brand:
                score += 7

            if word in category:
                score += 8

            if word in description:
                score += 4

            if word in specs:
                score += 2

        if score > 0:
            ranked.append(
                (
                    score,
                    float(product.get("rating", 0)),
                    product,
                )
            )

    ranked.sort(
        key=lambda x: (x[0], x[1]),
        reverse=True,
    )

    return [item[2] for item in ranked[:5]]


async def retrieve_documents(question: str):

    index, metadata = await get_or_build_index()

    docs = []

    if index is not None:

        model = get_embedding_model()

        vector = model.encode(
            [question],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        vector = np.asarray(vector, dtype=np.float32)

        scores, ids = index.search(vector, 10)

        SIMILARITY_THRESHOLD = 0.35

        for score, idx in zip(scores[0], ids[0]):

            if idx == -1:
                continue

            if score < SIMILARITY_THRESHOLD:
                continue

            docs.append(metadata[idx])

    if docs:
        print("\n========== RETRIEVED PRODUCTS ==========")

        for doc in docs:
            print(doc["content"])

        print("========================================")
        return docs

    logger.info("Using keyword fallback retrieval...")

    products = await db.products.find().to_list(1000)

    products = rank_products(question, products)

    if not products:
        return []

    return build_documents(products)


def build_prompt(question, docs):

    if docs:
        context = "\n\n".join(
            doc["content"]
            for doc in docs
        )
    else:
        context = "No matching product information available."


    return f"""
You are an intelligent AI shopping assistant.

Your job is to help customers with any e-commerce related question.

Rules:

1. Always answer the customer's question.
2. If product information is provided, use it.
3. If products are unavailable, answer using your general e-commerce knowledge.
4. Never say "I couldn't find any matching product in our catalog".
5. Never refuse a useful answer.

Product Information:

{context}


Customer Question:

{question}


Answer:
"""

async def retrieve_answer(question: str) -> str:

    if not settings.gemini_api_key:
        return "Gemini API key is missing."


    client = GeminiClient(
        api_key=settings.gemini_api_key
    )


    prompt = f"""
You are an AI e-commerce assistant.

Answer the user's question directly using your own knowledge.

You can help with:
- mobile phones
- laptops
- electronics
- product comparisons
- buying advice
- specifications
- features
- technology recommendations


Important rules:
- Do not mention any catalog.
- Do not mention database.
- Do not say "our store".
- Do not say "from our catalog".
- Provide a helpful answer.


User Question:

{question}


Answer:
"""


    try:

        logger.info("Calling Gemini...")

        answer = client.generate(prompt)

        if answer:
            return answer.strip()


    except Exception as e:

        logger.error(
            f"Gemini Error: {e}"
        )

        return f"Gemini Error: {e}"


    return "Sorry, I could not generate an answer."
def context_response(docs):

    lines = []

    for doc in docs:

        text = doc["content"]

        name = ""
        price = ""
        rating = ""
        stock = ""
        description = ""

        for line in text.splitlines():

            if line.startswith("Product"):
                name = line.split(":", 1)[1].strip()

            elif line.startswith("Price"):
                price = line.split(":", 1)[1].strip()

            elif line.startswith("Rating"):
                rating = line.split(":", 1)[1].strip()

            elif line.startswith("Stock"):
                stock = line.split(":", 1)[1].strip()

            elif line.startswith("Description"):
                description = line.replace("Description :", "").strip()

        lines.append(
            f"""• {name}

Price : {price}
Rating : ⭐ {rating}
Stock : {stock}

{description}
"""
        )

    return "\n".join(lines)

def find_field(content: str, field: str) -> str:

    prefix = f"{field} :"

    for line in content.splitlines():

        if line.startswith(prefix):
            return line.replace(prefix, "").strip()

    return ""


async def rebuild_index():

    logger.info("Rebuilding FAISS Index...")

    await build_faiss()

    logger.info("Finished rebuilding index.")