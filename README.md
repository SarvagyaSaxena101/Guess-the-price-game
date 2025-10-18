# Guess The Price — Streamlit Multiplayer Game

This project is a simple multiplayer "Guess The Price" game built with Streamlit. It fetches random items (image + price) from Sanity (GROQ) when configured, and falls back to placeholder images otherwise.

Features
- Create or join rooms with room codes
- Register with a player name
- Host starts and ends rounds
- Players submit guesses
- Scoring: 10 pts for closest, 5 for 2nd, 1 for 3rd

Quick start (Windows PowerShell)

1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. (Optional) Create a `.env` or set environment variables for Sanity

- SANITY_PROJECT_ID
- SANITY_DATASET (defaults to `production`)
- SANITY_TOKEN
 - FORCE_GROQ (optional): set to `1` or `true` to require GROQ to return a priced item. If enabled and no priced items are found, the app will raise an error.
 - GOOGLE_API_KEY and GOOGLE_CSE_ID (optional): if Sanity doesn't return a price, the app can try to infer a price from web search snippets.
If you want to use Groq (LLM) only and remove Sanity entirely, set the following environment variables instead:

- GROQ_API_URL: URL of your Groq-compatible LLM endpoint (example: http://localhost:11434/api/generate)
- GROQ_API_KEY: (optional) bearer token for the Groq endpoint
- FORCE_GROQ: set to `1` to require the Groq endpoint returns priced items

The app will call the Groq endpoint to generate items (title, price, image_url) in JSON format. If the model returns plain text, the client does some best-effort JSON extraction/parsing.

3. Run Streamlit

```powershell
streamlit run app.py
```

Notes
- This implementation stores all game state in-memory. For a production deployment use Redis or a database so multiple app instances can share state.
- The Sanity GROQ query expects documents of type `product` with `title`, `price`, and `image` fields. Adjust `sanity_client.py` to match your schema.
	- If you use Groq-only mode, ensure your Groq LLM returns a JSON object with `title`, `price`, and `image_url` or at least includes a $NN pattern the client can parse.
