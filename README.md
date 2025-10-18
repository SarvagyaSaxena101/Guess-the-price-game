# Guess The Price — Streamlit Multiplayer Game

This project is a simple multiplayer "Guess The Price" game built with Streamlit. It fetches random items from the Unsplash API and uses the Groq API to generate a realistic price.

## Features

- Create or join rooms with room codes
- Register with a player name
- Host starts and ends rounds
- Players submit guesses
- Scoring: 10 pts for closest, 5 for 2nd, 1 for 3rd

## Getting Started

1. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a `.env` file:**

   Create a `.env` file in the root of the project and add the following environment variables:

   ```
   UNSPLASH_API_KEY="YOUR_UNSPLASH_API_KEY"
   GROQ_API_URL="YOUR_GROQ_API_URL"
   GROQ_API_KEY="YOUR_GROQ_API_KEY"
   ```

3. **Run Streamlit:**

   ```bash
   streamlit run app.py
   ```

## Deployment

This app can be easily deployed to Streamlit Cloud. 

1. **Push your code to a GitHub repository.**
2. **Go to the Streamlit Cloud dashboard and create a new app.**
3. **Connect your GitHub repository and select the `main` branch.**
4. **Set the environment variables in the advanced settings.**
5. **Deploy the app!**

## Notes

- This implementation stores all game state in-memory. For a production deployment, you should use a database like Redis so that multiple app instances can share state.
- The app uses the Unsplash API to fetch random images of items. You will need to create a free developer account to get an API key.
- The app uses the Groq API to generate a realistic price for the items. You will need to create a free account to get an API key.