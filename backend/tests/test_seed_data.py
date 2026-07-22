import json
from pathlib import Path


def test_product_seed_file_exists():
    path = Path(__file__).resolve().parents[1] / "app" / "data" / "products.json"
    assert path.exists()
    content = json.loads(path.read_text(encoding="utf-8"))
    assert len(content) == 100
