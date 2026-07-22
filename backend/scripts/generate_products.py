import json
from pathlib import Path

categories = {
    "Laptops": [
        {"brand": "ApexTech", "base": "Apex"},
        {"brand": "NeoCore", "base": "Neo"},
        {"brand": "TitanBook", "base": "Titan"},
        {"brand": "Quantum", "base": "Quantum"},
        {"brand": "Stratus", "base": "Stratus"}
    ],
    "Mobiles": [
        {"brand": "Stellar", "base": "Stellar"},
        {"brand": "Pulse", "base": "Pulse"},
        {"brand": "Orbit", "base": "Orbit"},
        {"brand": "Horizon", "base": "Horizon"},
        {"brand": "Samsung", "base": "s-26 ultra"}
    ],
    "Shoes": [
        {"brand": "Velocity", "base": "Velocity"},
        {"brand": "Stride", "base": "Stride"},
        {"brand": "AeroFit", "base": "Aero"},
        {"brand": "Trailblaze", "base": "Trail"},
        {"brand": "UrbanRun", "base": "Urban"}
    ],
    "Headphones": [
        {"brand": "AuraSound", "base": "Aura"},
        {"brand": "HushPro", "base": "Hush"},
        {"brand": "ClearWave", "base": "Clear"},
        {"brand": "PulseAudio", "base": "Pulse"},
        {"brand": "EchoBound", "base": "Echo"}
    ],
    "Televisions": [
        {"brand": "VisionMax", "base": "Vision"},
        {"brand": "PureView", "base": "Pure"},
        {"brand": "LumaTech", "base": "Luma"},
        {"brand": "CinemaX", "base": "Cinema"},
        {"brand": "Spectrum", "base": "Spectrum"}
    ],
    "Smart Watches": [
        {"brand": "PulseSync", "base": "Pulse"},
        {"brand": "ChronoEdge", "base": "Chrono"},
        {"brand": "FitOrbit", "base": "Fit"},
        {"brand": "TempoGear", "base": "Tempo"},
        {"brand": "VivaTime", "base": "Viva"}
    ],
    "Tablets": [
        {"brand": "NoteFlex", "base": "Note"},
        {"brand": "SlateOne", "base": "Slate"},
        {"brand": "ProPad", "base": "Pro"},
        {"brand": "Canvas", "base": "Canvas"},
        {"brand": "Glide", "base": "Glide"}
    ],
    "Cameras": [
        {"brand": "FocusPro", "base": "Focus"},
        {"brand": "LensCraft", "base": "Lens"},
        {"brand": "CaptureX", "base": "Capture"},
        {"brand": "ViewLens", "base": "View"},
        {"brand": "Photon", "base": "Photon"}
    ],
    "Gaming Accessories": [
        {"brand": "StrataGear", "base": "Strata"},
        {"brand": "PulseAction", "base": "Pulse"},
        {"brand": "NexuPlay", "base": "Nexu"},
        {"brand": "ArenaTech", "base": "Arena"},
        {"brand": "FluxPro", "base": "Flux"}
    ],
    "Fashion": [
        {"brand": "EthosWear", "base": "Ethos"},
        {"brand": "LuxeLine", "base": "Luxe"},
        {"brand": "UrbanWeave", "base": "Urban"},
        {"brand": "SilkRoad", "base": "Silk"},
        {"brand": "MetroTone", "base": "Metro"}
    ]
}

spec_templates = {
    "Laptops": [
        ("Processor", ["Intel Core i7-13620H", "Intel Core i9-14900H", "AMD Ryzen 9 7945HX", "AMD Ryzen 7 7840HS"]),
        ("Graphics", ["NVIDIA GeForce RTX 4060", "NVIDIA GeForce RTX 4070", "AMD Radeon RX 7800M"]),
        ("Memory", ["16GB DDR5", "32GB DDR5", "24GB DDR5"]),
        ("Storage", ["512GB NVMe SSD", "1TB NVMe SSD", "2TB NVMe SSD"]),
        ("Display", ["14-inch QHD 240Hz", "16-inch WQXGA 165Hz", "15.6-inch FHD 240Hz"]),
        ("Battery", ["72Wh", "82Wh", "68Wh"])
    ],
    "Mobiles": [
        ("Display", ["6.8-inch AMOLED", "6.7-inch OLED", "6.5-inch FHD+ AMOLED"]),
        ("Processor", ["Qualcomm Snapdragon 8 Gen 3", "MediaTek Dimensity 9300", "Apple A17 Bionic"]),
        ("RAM", ["8GB", "12GB", "16GB"]),
        ("Storage", ["128GB", "256GB", "512GB"]),
        ("Camera", ["200MP + 16MP + 12MP", "108MP + 12MP + 8MP", "50MP + 12MP + 10MP"]),
        ("Battery", ["5000mAh", "5200mAh", "4800mAh"])
    ],
    "Shoes": [
        ("Upper", ["Breathable mesh", "Synthetic knit", "Leather mesh blend"]),
        ("Midsole", ["Energy-return foam", "Cushioned EVA", "Responsive cushion"]),
        ("Outsole", ["Rubber traction", "Grip endurance", "Dual-density tread"]),
        ("Weight", ["240g", "260g", "225g"]),
        ("Fit", ["Regular", "Slim", "Wide"])
    ],
    "Headphones": [
        ("Type", ["Over-ear", "On-ear", "In-ear"]),
        ("Noise Cancellation", ["Active", "Passive", "Hybrid"]),
        ("Battery Life", ["40 hours", "35 hours", "50 hours"]),
        ("Connectivity", ["Bluetooth 5.3", "Bluetooth 5.2", "Bluetooth 5.4"]),
        ("Weight", ["295g", "280g", "310g"])
    ],
    "Televisions": [
        ("Display Size", ["55-inch", "65-inch", "75-inch"]),
        ("Resolution", ["4K UHD", "8K UHD"]),
        ("HDR", ["HDR10+", "Dolby Vision", "HDR10"]),
        ("Smart TV", ["Yes"]),
        ("Refresh Rate", ["120Hz", "240Hz"])
    ],
    "Smart Watches": [
        ("Display", ["1.9-inch AMOLED", "1.78-inch OLED", "1.85-inch AMOLED"]),
        ("Sensors", ["Heart rate, SpO2, GPS", "ECG, GPS, Sleep", "Heart rate, GPS, Compass"]),
        ("Battery Life", ["18 hours", "30 hours", "14 days"]),
        ("Connectivity", ["Bluetooth 5.2", "Bluetooth 5.3", "LTE optional"]),
        ("Water Resistance", ["50m", "5ATM", "IP68"])
    ],
    "Tablets": [
        ("Display", ["11-inch Liquid Retina", "12.9-inch Mini-LED", "10.9-inch IPS"]),
        ("Processor", ["Apple M2", "Qualcomm Snapdragon 8cx Gen 3", "MediaTek Kompanio 1380"]),
        ("RAM", ["8GB", "12GB", "16GB"]),
        ("Storage", ["128GB", "256GB", "512GB"]),
        ("Connectivity", ["Wi-Fi 6", "Wi-Fi 6E", "5G optional"])
    ],
    "Cameras": [
        ("Sensor", ["24MP CMOS", "45MP full-frame", "33MP APS-C"]),
        ("Lens", ["24-70mm kit", "18-55mm kit", "24-105mm kit"]),
        ("Video", ["4K 60fps", "6K 30fps", "1080p 120fps"]),
        ("Stabilization", ["Optical", "Electronic", "Dual"]),
        ("ISO Range", ["100-51200", "50-204800", "100-102400"])
    ],
    "Gaming Accessories": [
        ("Type", ["Mechanical keyboard", "Gaming mouse", "RGB headset", "Controller"]),
        ("Connectivity", ["Wired USB-C", "Wireless 2.4GHz", "Bluetooth"]),
        ("Special Feature", ["Custom macros", "Adjustable DPI", "Surround sound", "Haptic feedback"]),
        ("Compatibility", ["PC/PS5/Xbox", "PC/Mac", "Console/PC"]),
        ("Lighting", ["RGB", "ARGB", "Static"])
    ],
    "Fashion": [
        ("Fabric", ["Cotton blend", "Microfiber", "Silk blend", "Denim"]),
        ("Style", ["Casual", "Formal", "Athleisure", "Streetwear"]),
        ("Fit", ["Slim", "Regular", "Relaxed"]),
        ("Care", ["Machine wash", "Hand wash", "Dry clean"]),
        ("Color", ["Black", "Blue", "Grey", "White", "Olive"])
    ]
}

def create_description(category: str, name: str, brand: str) -> str:
    if category == "Laptops":
        return f"{name} is a performance laptop built for professionals and gamers, featuring advanced cooling, a vivid display, and long battery life."
    if category == "Mobiles":
        return f"{name} brings flagship-level performance, an immersive display, and a pro-grade camera setup in a slim chassis."
    if category == "Shoes":
        return f"{name} offers comfortable support, dynamic cushioning, and durable stability for everyday wear and active training."
    if category == "Headphones":
        return f"{name} delivers rich audio clarity, noise isolation, and extended wireless playback for immersive listening."
    if category == "Televisions":
        return f"{name} delivers bright cinematic imagery, smart connectivity, and a sleek bezel for modern living rooms."
    if category == "Smart Watches":
        return f"{name} blends fitness tracking, health monitoring, and smartwatch convenience in a stylish wearable."
    if category == "Tablets":
        return f"{name} is a versatile tablet for productivity and entertainment with a responsive touchscreen and fast processor."
    if category == "Cameras":
        return f"{name} captures stunning photos and video with precise autofocus and advanced stabilization."
    if category == "Gaming Accessories":
        return f"{name} elevates your gaming setup with responsive performance and customizable controls."
    return f"{name} offers premium fabric, refined tailoring, and comfortable everyday wear for trend-conscious customers."

entries = []

for category, brands in categories.items():
    for brand_idx, brand_info in enumerate(brands):
        for variant in range(1, 3):
            name = f"{brand_info['base']} {category[:-1]} {brand_idx*2 + variant}"
            if category == "Laptops":
                price = round(1099 + brand_idx * 200 + variant * 150, 2)
            elif category == "Mobiles":
                price = round(549 + brand_idx * 120 + variant * 80, 2)
            elif category == "Shoes":
                price = round(79 + brand_idx * 15 + variant * 10, 2)
            elif category == "Headphones":
                price = round(149 + brand_idx * 35 + variant * 40, 2)
            elif category == "Televisions":
                price = round(499 + brand_idx * 120 + variant * 90, 2)
            elif category == "Smart Watches":
                price = round(179 + brand_idx * 35 + variant * 25, 2)
            elif category == "Tablets":
                price = round(329 + brand_idx * 70 + variant * 50, 2)
            elif category == "Cameras":
                price = round(599 + brand_idx * 130 + variant * 90, 2)
            elif category == "Gaming Accessories":
                price = round(59 + brand_idx * 25 + variant * 20, 2)
            else:
                price = round(49 + brand_idx * 18 + variant * 12, 2)

            discount = round(min(25.0, 5 + brand_idx * 2 + variant), 2)
            rating = round(min(4.9, 3.8 + (brand_idx + variant) * 0.15), 1)
            stock = 120 + brand_idx * 15 + variant * 8 if category == "Fashion" else 45 + brand_idx * 20 + variant * 10

            specifications = {
                key: options[(brand_idx + variant) % len(options)]
                for key, options in spec_templates[category]
            }

            images = [
                f"/products/{category.lower().replace(' ', '-')}/{name.lower().replace(' ', '-')}-{i}.jpg"
                for i in range(1, 3)
            ]

            entries.append({
                "name": name,
                "brand": brand_info['brand'],
                "category": category,
                "price": price,
                "discount": discount,
                "description": create_description(category, name, brand_info['brand']),
                "specifications": specifications,
                "rating": rating,
                "stock": stock,
                "images": images
            })

output_path = Path(__file__).resolve().parents[1] / "app" / "data" / "products.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open('w', encoding='utf-8') as f:
    json.dump(entries, f, indent=2)

print(f'Wrote {len(entries)} products to {output_path}')
