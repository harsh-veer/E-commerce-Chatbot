import json
import logging
import os
import re
import sys
from datetime import datetime
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import faiss
import numpy as np
import requests

from app.config.settings import settings
from app.database.client import db
from app.rag.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

INDEX_DIR = "faiss_index"
INDEX_FILE = os.path.join(INDEX_DIR, "index.faiss")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.json")


def get_gemini_embeddings_batch(texts: list[str]) -> np.ndarray | None:
    api_key = settings.gemini_api_key
    if not api_key or not texts:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents?key={api_key}"
        all_vecs = []
        chunk_size = 50
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i : i + chunk_size]
            reqs = [
                {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": t}]}}
                for t in chunk
            ]
            res = requests.post(url, json={"requests": reqs}, timeout=30)
            if res.status_code == 200:
                data = res.json()
                for emb in data.get("embeddings", []):
                    all_vecs.append(emb.get("values", []))
            else:
                logger.warning(f"Batch embedding failed with status {res.status_code}: {res.text[:150]}")
                return None

        if not all_vecs or len(all_vecs) != len(texts):
            return None

        arr = np.array(all_vecs, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms
    except Exception as e:
        logger.error(f"Error generating Gemini batch embeddings: {e}")
        return None


def get_gemini_single_embedding(text: str) -> np.ndarray | None:
    api_key = settings.gemini_api_key
    if not api_key or not text:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
        res = requests.post(url, json={"content": {"parts": [{"text": text}]}}, timeout=10)
        if res.status_code == 200:
            vals = res.json().get("embedding", {}).get("values", [])
            if vals:
                arr = np.array(vals, dtype=np.float32)
                norm = np.linalg.norm(arr)
                return (arr / norm) if norm > 0 else arr
        else:
            logger.warning(f"Single embedding returned status {res.status_code}: {res.text[:150]}")
    except Exception as e:
        logger.error(f"Error generating Gemini query embedding: {e}")
    return None


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
            for k, v in product.get("specifications", {}).items()
        )

        category = product.get("category", "")
        network_tag = "Network: 5G / LTE Supported\n" if category.lower() in ["mobiles", "phones", "cellphones", "smartphones"] else ""

        price_val = float(product.get("price", 0))
        price_display = f"₹{int(price_val):,}" if price_val > 0 else "₹0"
        docs.append(
            {
                "id": str(product["_id"]),
                "name": product["name"],
                "brand": product["brand"],
                "category": product["category"],
                "rating": float(product.get("rating", 0)),
                "price": price_val,
                "stock": product.get("stock", 0),
                "content": f"""
Product : {product['name']}
Brand : {product['brand']}
Category : {product['category']}
Price : {price_display}
Discount : {product.get('discount', 0)}%
Rating : {product.get('rating', 0)}
Stock : {product.get('stock', 0)}
{network_tag}
Description :
{product.get('description', '')}

Specifications

{specs}
""",
            }
        )
    return docs


def save_index(index, metadata):
    os.makedirs(INDEX_DIR, exist_ok=True)
    if index is not None:
        faiss.write_index(index, INDEX_FILE)
    elif os.path.exists(INDEX_FILE):
        try:
            os.remove(INDEX_FILE)
        except OSError:
            pass

    with open(METADATA_FILE, "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=2)


def load_index():
    metadata = None
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, encoding="utf8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = None

    if not os.path.exists(INDEX_FILE):
        return None, metadata

    try:
        index = faiss.read_index(INDEX_FILE)
        return index, metadata
    except Exception as e:
        logger.error(f"Failed to read FAISS index: {e}")
        return None, metadata


async def build_faiss():
    logger.info("Building FAISS Index using Gemini Embeddings...")
    products = await db.products.find().to_list(1000)
    if not products:
        logger.info("No products found in DB for indexing.")
        return

    docs = build_documents(products)
    vectors = get_gemini_embeddings_batch([doc["content"] for doc in docs])

    if vectors is not None and len(vectors) > 0:
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        save_index(index, docs)
        logger.info(f"FAISS Index Created with {len(docs)} products.")
    else:
        logger.warning("Gemini embeddings unavailable; saving metadata for keyword retrieval fallback.")
        save_index(None, docs)


async def get_or_build_index():
    index, metadata = load_index()
    try:
        mongo_count = await db.products.count_documents({})
        if metadata is None or (metadata is not None and len(metadata) != mongo_count):
            logger.info("Index missing or product count mismatch. Rebuilding...")
            await build_faiss()
            return load_index()
    except Exception as err:
        logger.error(f"Error checking mongo count for index sync: {err}")

    if index is not None or metadata is not None:
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

    if index is not None and metadata:
        query_vector = get_gemini_single_embedding(question)
        if query_vector is not None:
            vector = np.asarray([query_vector], dtype=np.float32)
            scores, ids = index.search(vector, min(30, len(metadata)))

            SIMILARITY_THRESHOLD = 0.20
            raw_candidates = []
            for score, idx in zip(scores[0], ids[0]):
                if idx == -1 or idx >= len(metadata):
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
                candidates_to_sort.sort(
                    key=lambda d: (d.get("rating", 0), d.get("price", 0), d.get("vector_score", 0)),
                    reverse=True,
                )
                docs = candidates_to_sort[:6]

    if docs:
        logger.info(f"Retrieved {len(docs)} matching products from catalog.")
        for doc in docs:
            p_val = doc.get("price", 0)
            p_str = f"₹{int(p_val):,}" if isinstance(p_val, (int, float)) and p_val > 0 else f"₹{p_val}"
            logger.info(f"- {doc['name']} | Rating: {doc.get('rating')} | Price: {p_str}")
        return docs

    logger.info("Using keyword fallback retrieval...")
    products = await db.products.find().to_list(1000)
    products = rank_products(question, products)
    if not products:
        return []
    return build_documents(products)


def build_prompt(question: str, docs: list[dict] = None) -> str:
    current_year = datetime.now().year
    catalog_context = ""
    if docs:
        context_lines = []
        for doc in docs:
            raw_price = doc.get("price", 0)
            try:
                price_num = float(raw_price)
                price_str = f"₹{int(price_num):,}" if price_num > 0 else "N/A"
            except (ValueError, TypeError):
                price_str = f"₹{raw_price}"
            context_lines.append(
                f"- Product: {doc.get('name')} | Brand: {doc.get('brand')} | Category: {doc.get('category')} | Price: {price_str} | Rating: ⭐{doc.get('rating')} | Stock: {doc.get('stock')}\n  Details: {doc.get('content', '').strip()}"
            )
        catalog_context = f"\nLatest Store Catalog Products Found in Database:\n" + "\n".join(context_lines) + "\n"

    return f"""You are an intelligent, expert AI E-commerce & Product Assistant (Current Context Year: {current_year}).

User Question: {question}
{catalog_context}
Instructions:
1. Provide the newest, most up-to-date, and accurate real-world product recommendations, specifications, features, price comparisons, or buying advice available for {current_year}.
2. If store catalog products are listed in the context above, seamlessly integrate relevant items into your answer, citing their specs, exact price, and current stock status. NOTE: Store catalog prices are ALREADY in Indian Rupees (INR / ₹) — use the EXACT price as given in the context and do NOT multiply, convert, or inflate it.
3. ALWAYS state all product prices, price ranges, and estimated costs in Indian Rupees (INR / ₹, e.g., ₹3,49,900 or ₹1,44,900) instead of US Dollars ($) or other currencies.
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
        price = doc.get("price", 0)
        try:
            price_display = f"₹{int(float(price)):,}"
        except Exception:
            price_display = f"₹{price}"
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
            f"* **Price:** {price_display} | **Rating:** ⭐ {rating} | **Stock:** {stock}\n"
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