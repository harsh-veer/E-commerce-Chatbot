# AI-Powered E-commerce Product Q&A Bot Backend

This repository contains the backend for an AI-powered e-commerce retrieval-augmented generation (RAG) chatbot.

## Features

- FastAPI backend with modular routing
- MongoDB Atlas integration using Motor
- JWT authentication endpoints
- Product CRUD APIs
- Chat endpoint with RAG pipeline using LangChain and FAISS

## Setup

1. Create a `.env` file at the repository root.
2. Set environment variables:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net
MONGO_DB=ecommerce_bot
JWT_SECRET=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

3. Install dependencies:

```bash
python -m pip install -e .
```

4. Run the application:

```bash
uvicorn app.main:app --reload --port 8000
```

## Seeding Products

To populate the product catalog, run:

```bash
python -m app.services.seed_products
```

## API Endpoints

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/products`
- `GET /api/products/{id}`
- `POST /api/products`
- `PUT /api/products/{id}`
- `DELETE /api/products/{id}`
- `POST /api/chat`
- `GET /api/chat/history`
