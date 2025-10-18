import os
import json
import requests
import random
import re
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = os.getenv('GROQ_API_URL')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL_ID = os.getenv('GROQ_MODEL_ID')
UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY')

ITEM_KEYWORDS = [
    "laptop", "smartphone", "headphones", "camera", "watch", "backpack", "shoes",
    "t-shirt", "jeans", "book", "chair", "desk", "lamp", "keyboard", "mouse"
]

def _get_random_item_image_url() -> Optional[Dict]:
    """Fetch a random image URL from Unsplash based on a keyword."""
    if not UNSPLASH_API_KEY:
        print("UNSPLASH_API_KEY not set, cannot fetch item image.")
        return None

    keyword = random.choice(ITEM_KEYWORDS)
    try:
        url = f"https://api.unsplash.com/photos/random?query={keyword}&client_id={UNSPLASH_API_KEY}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return {
            "image_url": data['urls']['regular'],
            "keyword": keyword
        }
    except Exception as e:
        print(f"Failed to fetch image from Unsplash: {e}")
        return None

def _try_parse_json(text: str) -> Optional[Dict]:
    text = text.strip()
    # Try to find first JSON object in the output
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    s = m.group(1) if m else text
    try:
        return json.loads(s)
    except Exception:
        return None

def fetch_from_groq_prompt(prompt: str) -> Optional[str]:
    """Send prompt to Groq-compatible endpoint and return raw text output (best effort)."""
    headers = {}
    if GROQ_API_KEY:
        headers['Authorization'] = f'Bearer {GROQ_API_KEY}'

    # Helper to call an endpoint and extract text
    def _call_endpoint(url: str) -> Optional[str]:
        try:
            resp = requests.post(url, json={'prompt': prompt, 'max_tokens': 200}, headers=headers, timeout=15)
            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception:
                return resp.text
            # OpenAI-like
            if isinstance(data, dict):
                if 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                    return data['choices'][0].get('text') or data['choices'][0].get('message', {}).get('content')
                if 'output' in data:
                    out = data['output']
                    if isinstance(out, list) and out:
                        if isinstance(out[0], dict) and 'content' in out[0]:
                            return out[0]['content']
                        return out[0]
                if 'text' in data:
                    return data['text']
            return resp.text
        except Exception:
            try:
                # Try GET as fallback
                resp = requests.get(url, params={'prompt': prompt}, headers=headers, timeout=15)
                resp.raise_for_status()
                return resp.text
            except Exception:
                return None

    # 1) If a full API URL is provided, try that first
    if GROQ_API_URL:
        out = _call_endpoint(GROQ_API_URL)
        if out:
            return out

    # 2) If a model id is provided but full URL isn't, try common Groq endpoint patterns
    if GROQ_MODEL_ID:
        candidates = [
            f"https://api.groq.ai/v1/models/{GROQ_MODEL_ID}/invoke",
            f"https://api.groq.ai/v1/models/{GROQ_MODEL_ID}/predict",
            f"https://api.groq.ai/v1/models/{GROQ_MODEL_ID}:predict",
            f"https://api.groq.ai/v1/models/{GROQ_MODEL_ID}:invoke",
            f"https://api.groq.ai/v1/models/{GROQ_MODEL_ID}/completions",
        ]
        for url in candidates:
            out = _call_endpoint(url)
            if out:
                return out

    # 3) Nothing worked
    return None

def fetch_price_from_groq(title: str, image_url: Optional[str] = None) -> Optional[float]:
    """Ask the Groq LLM for a reasonable price for the given title (and optional image)."""
    # Create a deterministic but varied prompt
    example_items = [
        "Wireless Bluetooth Headphones - $79.99",
        "Stainless Steel Travel Mug - $24.50",
        "4K USB Webcam - $129.00",
    ]
    prompt = (
        "You are an assistant that returns a JSON object with fields: title (string), price (number), image_url (string URL or empty)."
        " Return only the JSON object.\n"
        f"Item title: {title}\n"
    )
    if image_url:
        prompt += f"Image URL: {image_url}\n"
    prompt += "Provide a realistic retail price in USD as the 'price' field. Example outputs: " + ", ".join(example_items)

    raw = fetch_from_groq_prompt(prompt)
    if not raw:
        return None
    parsed = _try_parse_json(raw)
    if parsed and 'price' in parsed:
        try:
            return float(parsed['price'])
        except Exception:
            return None

    # If parsing failed, try to extract $NNN pattern
    m = re.search(r"\$\s?([0-9]{1,3}(?:[\,0-9]*)(?:\.[0-9]{1,2})?)", raw)
    if m:
        try:
            return float(m.group(1).replace(',', ''))
        except Exception:
            return None
    return None

def fetch_random_item() -> Dict:
    """Use Groq LLM to produce a plausible item with title, price and image_url."""
    image_data = _get_random_item_image_url()
    if not image_data:
        return {
            'title': 'Fallback Item',
            'price': 123.45,
            'image_url': 'https://via.placeholder.com/400'
        }

    image_url = image_data['image_url']
    keyword = image_data['keyword']

    if not GROQ_API_URL:
        print("GROQ_API_URL not set, using fallback item")
        return {
            'title': keyword.title(),
            'price': round(random.uniform(10, 500), 2),
            'image_url': image_url
        }

    # Prompt the model to produce a JSON object
    prompt = (
        "Produce a JSON object with fields: title (string), price (number)."
        f" The user has provided this image of a {keyword}: {image_url}"
        " Choose a realistic retail product and a reasonable USD price. Return only the JSON object."
    )
    raw = fetch_from_groq_prompt(prompt)
    if not raw:
        raise RuntimeError('Groq endpoint did not return a response')
    parsed = _try_parse_json(raw)
    if parsed:
        title = parsed.get('title') or f"Generated Item #{random.randint(1,999)}"
        price = None
        if 'price' in parsed:
            try:
                price = float(parsed['price'])
            except Exception:
                price = None
        return {'title': title, 'price': price, 'image_url': image_url}

    # If parsing failed, attempt to extract fields from the raw text
    # title: first line
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    title = lines[0] if lines else f"Generated Item #{random.randint(1,999)}"
    # price extraction
    m = re.search(r"\$\s?([0-9]{1,3}(?:[\,0-9]*)(?:\.[0-9]{1,2})?)", raw)
    price = float(m.group(1).replace(',', '')) if m else None
    return {'title': title, 'price': price, 'image_url': image_url}

if __name__ == '__main__':
    print(fetch_random_item())
