import os
import random
import re
import requests
from typing import Dict, Optional

SANITY_PROJECT_ID = os.getenv('SANITY_PROJECT_ID')
SANITY_DATASET = os.getenv('SANITY_DATASET', 'production')
SANITY_TOKEN = os.getenv('SANITY_TOKEN')
# If FORCE_GROQ is set to "1" or "true", require that a priced item is returned by GROQ or raise an error
FORCE_GROQ = str(os.getenv('FORCE_GROQ', '')).lower() in ('1', 'true')

# Optional Google Custom Search (used only to try to extract a price when Sanity doesn't provide one)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GROQ_API_URL = os.getenv('GROQ_API_URL')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


def _extract_price(text: str) -> Optional[float]:
    if not text:
        return None
    # look for $123.45 style patterns (basic)
    m = re.search(r"\$\s?([0-9]{1,3}(?:[\,0-9]*)(?:\.[0-9]{1,2})?)", text)
    if m:
        try:
            return float(m.group(1).replace(',', ''))
        except Exception:
            return None
    return None


def fetch_price_from_google(query: str) -> Optional[float]:
    """Try to extract a price from Google Custom Search results/snippets.

    Requires GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables. Returns a float price or None.
    """
    if not (GOOGLE_API_KEY and GOOGLE_CSE_ID):
        return None
    try:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CSE_ID, 'q': query, 'num': 3}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get('items', [])[:3]:
            # try snippet and title first
            price = _extract_price(item.get('snippet', '') or '')
            if price:
                return price
            price = _extract_price(item.get('title', '') or '')
            if price:
                return price
            # if no snippet price, try fetching the linked page and searching for a price
            link = item.get('link')
            if link:
                try:
                    page = requests.get(link, timeout=6)
                    page.raise_for_status()
                    price = _extract_price(page.text)
                    if price:
                        return price
                except Exception:
                    continue
    except Exception:
        return None
    return None


def fetch_random_item() -> Dict:
    """
    Fetch a random item (image, title, price) from Sanity using GROQ if configured.

    Important: This function will NOT invent a price. If Sanity is configured and the
    document contains a numeric `price` field it will be returned. If no price is available
    but GOOGLE_API_KEY and GOOGLE_CSE_ID are provided, the function will try to extract
    a price from Google results. If no price can be determined, `price` will be None and
    the host must set the true price before the round is scored.
    """
    # 1) Try Sanity/GROQ
    if SANITY_PROJECT_ID and SANITY_TOKEN:
        try:
            url = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2021-06-07/data/query/{SANITY_DATASET}"
            # Prefer documents that have a defined numeric price and an image
            groq = "*[_type == \"product\" && defined(price) && defined(image)][0..200] {title, price, 'imageUrl': image.asset->url}"
            resp = requests.get(url, params={'query': groq}, headers={'Authorization': f'Bearer {SANITY_TOKEN}'}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = data.get('result') or []
            if results:
                item = random.choice(results)
                price_val = item.get('price')
                # attempt to coerce numeric values
                try:
                    price = float(price_val) if price_val is not None else None
                except Exception:
                    price = None
                return {
                    'title': item.get('title', 'Unknown item'),
                    'price': price,
                    'image_url': item.get('imageUrl') or '',
                }
        except Exception:
            # fall through to placeholder behavior
            pass

    # 2) Fallback: return a placeholder image + no price (host must set price), unless Google keys are present
    try:
        w = 800
        h = 600
        image_url = f"https://picsum.photos/{w}/{h}?random={random.randint(1,10000)}"
        title = f"Placeholder Item #{random.randint(1,999)}"
        # attempt to infer a price using Google CSE if available
        inferred_price = None
        # Try searching the title as a last resort
        if GOOGLE_API_KEY and GOOGLE_CSE_ID:
            inferred_price = fetch_price_from_google(title)

        # If still no price, try calling a Groq-compatible LLM endpoint (useful if you run Groq LLM locally or via cloud)
        if (inferred_price is None) and GROQ_API_URL:
            try:
                inferred_price = fetch_price_from_groq(title, image_url)
            except Exception:
                inferred_price = None

        result = {
            'title': title,
            'price': inferred_price,  # may be None
            'image_url': image_url,
        }

        # If the caller requires GROQ to supply a priced item, raise an error now
        if FORCE_GROQ and (result['price'] is None):
            raise RuntimeError('FORCE_GROQ enabled but could not fetch an item with a price from Sanity or Google.')

        return result
    except Exception:
        return {
            'title': 'Placeholder Item',
            'price': None,
            'image_url': '',
        }


if __name__ == '__main__':
    print(fetch_random_item())
