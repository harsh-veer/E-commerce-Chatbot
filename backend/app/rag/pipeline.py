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

        category = product.get("category", "")
        network_tag = "Network: 5G / LTE Supported\n" if category.lower() in ["mobiles", "phones", "cellphones", "smartphones"] else ""

        docs.append(
            {
                "id": str(product["_id"]),
                "name": product["name"],
                "brand": product["brand"],
                "category": product["category"],
                "rating": float(product.get("rating", 0)),
                "price": float(product.get("price", 0)),
                "content":
f"""
Product : {product['name']}
Brand : {product['brand']}
Category : {product['category']}
Price : ${product['price']}
Discount : {product['discount']}%
Rating : {product['rating']}
Stock : {product['stock']}
{network_tag}
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

    try:
        mongo_count = await db.products.count_documents({})
        if index is None or metadata is None or (metadata is not None and len(metadata) != mongo_count):
            logger.info("FAISS index missing or database product count mismatch. Rebuilding FAISS Index...")
            await build_faiss()
            return load_index()
    except Exception as err:
        logger.error(f"Error checking mongo product count for index sync: {err}")

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

        scores, ids = index.search(vector, 30)

        SIMILARITY_THRESHOLD = 0.20

        raw_candidates = []
        for score, idx in zip(scores[0], ids[0]):

            if idx == -1:
                continue

            if score < SIMILARITY_THRESHOLD:
                continue

            doc_item = dict(metadata[idx])
            doc_item["vector_score"] = float(score)
            raw_candidates.append(doc_item)

        if raw_candidates:
            question_lower = question.lower()
            matching_category_docs = []

            for doc in raw_candidates:
                cat = doc.get("category", "").lower()
                if ("mobile" in question_lower or "phone" in question_lower or "smartphone" in question_lower or "5g" in question_lower) and cat == "mobiles":
                    matching_category_docs.append(doc)
                elif ("laptop" in question_lower or "notebook" in question_lower) and cat == "laptops":
                    matching_category_docs.append(doc)
                elif ("headphone" in question_lower or "earbud" in question_lower or "noise" in question_lower) and cat == "headphones":
                    matching_category_docs.append(doc)
                elif ("watch" in question_lower or "fitness" in question_lower) and cat in ["smart watches", "watches"]:
                    matching_category_docs.append(doc)
                elif ("tv" in question_lower or "television" in question_lower) and cat == "televisions":
                    matching_category_docs.append(doc)

            candidates_to_sort = matching_category_docs if matching_category_docs else raw_candidates

            # Sort candidate products by rating descending, price descending (latest/top models have highest ratings & price)
            candidates_to_sort.sort(
                key=lambda d: (d.get("rating", 0), d.get("price", 0), d.get("vector_score", 0)),
                reverse=True
            )
            docs = candidates_to_sort[:6]

    if docs:
        print("\n========== RETRIEVED PRODUCTS ==========")

        for doc in docs:
            print(f"{doc['name']} | Rating: {doc.get('rating')} | Price: ${doc.get('price')}")

        print("========================================")
        return docs

    logger.info("Using keyword fallback retrieval...")

    products = await db.products.find().to_list(1000)

    products = rank_products(question, products)

    if not products:
        return []

    return build_documents(products)


from datetime import datetime

def build_prompt(question: str, docs: list[dict] = None) -> str:
    current_year = datetime.now().year
    catalog_context = ""
    if docs:
        context_lines = []
        for doc in docs:
            price_usd = float(doc.get("price", 0))
            price_inr = int(price_usd * 83) if price_usd > 0 else 0
            price_str = f"₹{price_inr:,}" if price_inr > 0 else "N/A"
            context_lines.append(
                f"- Product: {doc.get('name')} | Brand: {doc.get('brand')} | Category: {doc.get('category')} | Price: {price_str} | Rating: ⭐{doc.get('rating')} | Stock: {doc.get('stock')}\n  Details: {doc.get('content', '').strip()}"
            )
        catalog_context = f"\nLatest Store Catalog Products Found in Database:\n" + "\n".join(context_lines) + "\n"

    return f"""You are an intelligent, expert AI E-commerce & Product Assistant (Current Context Year: {current_year}).

User Question: {question}
{catalog_context}
Instructions:
1. Provide the newest, most up-to-date, and accurate real-world product recommendations, specifications, features, price comparisons, or buying advice available for {current_year}.
2. If store catalog products are listed in the context above, seamlessly integrate relevant items into your answer, citing their specs, exact price, and current stock status.
3. ALWAYS state all product prices, price ranges, and estimated costs in Indian Rupees (INR / ₹) instead of US Dollars ($) or other currencies.
4. Focus strictly on the latest, top-recommended real-world products (e.g. smartphones, laptops, smartwatches, headphones, gaming gear, electronics).
5. Structure the response clearly using clean Markdown bullet points, bold product titles, key specifications, and concise section headers.

Answer:
"""


async def retrieve_answer(question: str) -> str:
    docs = []
    try:
        docs = await retrieve_documents(question)
    except Exception as e:
        logger.error(f"Error retrieving catalog docs for RAG: {e}")

    prompt = build_prompt(question, docs)

    if not settings.gemini_api_key:
        return "I am an AI e-commerce assistant powered by Gemini. Please configure your GEMINI_API_KEY to start asking questions!"

    try:
        client = GeminiClient(api_key=settings.gemini_api_key)
        logger.info("Calling Gemini API with real-time context...")
        answer = client.generate(prompt)
        if answer:
            return answer.strip()
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return "Sorry, I encountered an issue retrieving the latest answer from Gemini API. Please check your network connection and API key."

    return "I am ready to help you with product details, specs, comparisons, or recommendations. How can I assist you today?"


async def retrieve_answer_stream(question: str):
    docs = []
    try:
        docs = await retrieve_documents(question)
    except Exception as e:
        logger.error(f"Error retrieving catalog docs for RAG stream: {e}")

    prompt = build_prompt(question, docs)

    if not settings.gemini_api_key:
        yield "I am an AI e-commerce assistant powered by Gemini. Please configure your GEMINI_API_KEY to start asking questions!"
        return

    try:
        client = GeminiClient(api_key=settings.gemini_api_key)
        logger.info("Calling Gemini API stream with real-time context...")
        has_content = False
        async for chunk in client.generate_stream(prompt):
            if chunk:
                has_content = True
                yield chunk

        if not has_content:
            yield "I am ready to help you with product details, specs, comparisons, or recommendations. How can I assist you today?"
    except Exception as e:
        logger.error(f"Gemini API Stream Error: {e}")
        yield "Sorry, I encountered an issue retrieving the streaming answer from Gemini API. Please check your network connection and API key."


def context_response(docs):

    lines = ["Here are the top matching products from our catalog:\n"]

    for doc in docs:
        text = doc["content"]

        name = doc.get("name", "")
        price = doc.get("price", "")
        rating = doc.get("rating", "")
        stock = ""
        description = ""

        for line in text.splitlines():
            if line.startswith("Stock"):
                stock = line.split(":", 1)[1].strip()
            elif line.startswith("Description"):
                description = line.replace("Description :", "").strip()

        lines.append(
            f"### **{name}**\n"
            f"* **Price:** ${price} | **Rating:** ⭐ {rating} | **Stock:** {stock}\n"
            f"* **Details:** {description}\n"
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