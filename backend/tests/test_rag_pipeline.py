import pytest

from app.rag.pipeline import build_documents_from_products, build_rag_index


@pytest.mark.asyncio
async def test_build_documents_from_products():
    sample_products = [
        {
            "_id": "123",
            "name": "Sample Product",
            "brand": "SampleBrand",
            "category": "Sample",
            "price": 99.99,
            "discount": 5,
            "description": "Sample description",
            "specifications": {"Feature": "Value"},
            "rating": 4.2,
            "stock": 10,
        }
    ]

    documents = build_documents_from_products(sample_products)
    assert len(documents) == 1
    assert "Sample Product" in documents[0].page_content


@pytest.mark.asyncio
async def test_build_rag_index_runs_without_products():
    await build_rag_index()
    assert True
