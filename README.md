# 🎮 Guess The Price — Streamlit Multiplayer Game 🎮

This project is a simple multiplayer "Guess The Price" game built with Streamlit. It fetches random items from the Unsplash API and uses the Groq API to generate a realistic price.

## 🚀 Try it now (Deployed link) 🚀

https://guess-the-price-game.streamlit.app/
it might take a little time to load but it will for sure broski.

## ✨ Features ✨

- **👨‍👩‍👧‍👦 Multiplayer Rooms:** Create your own private game room or join a friend's room using a unique room code.
- **⚡ Real-time Gameplay:** Play with your friends in real-time.
- **🖼️ Dynamic Item Generation:** The game fetches random item images from Unsplash and uses the Groq API to generate a realistic title and price for each round.
- **🏆 Scoring System:** Earn points based on how close your guess is to the actual price. The scoring is as follows:
    - 🥇 10 points for the closest guess.
    - 🥈 5 points for the second closest guess.
    - 🥉 1 point for the third closest guess.
- **👑 Host Controls:** The room's host can start and end rounds.
- **🎨 Simple UI:** A clean and simple user interface built with Streamlit.

## 🎲 How to Play 🎲

1.  **✍️ Enter Your Name:** Start by entering your player name in the sidebar.
2.  **🚪 Create or Join a Room:**
    - To create a room, click the "Create Room" button. A unique room code will be generated for you. Share this code with your friends so they can join.
    - To join a room, enter the room code your friend gave you and click the "Join Room" button.
3.  **▶️ Start the Game:** The host of the room can start the game by clicking the "Start Round" button.
4.  **💰 Guess the Price:** An image of an item will be displayed. Enter your guess for the price of the item and click "Submit Guess".
5.  **🛑 End of the Round:** The host can end the round by clicking the "End Round" button. The actual price will be revealed, and points will be awarded to the players with the closest guesses.
6.  **🔄 Next Round:** The host can start a new round at any time.

## 🛠️ Technical Stack 🛠️

- **🖥️ Frontend:** [Streamlit](https://streamlit.io/)
- **🐍 Backend:** Python
- **🔌 APIs:**
    - [Groq API](https://wow.groq.com/): For generating realistic item titles and prices.
    - [Unsplash API](https://unsplash.com/developers): For fetching random item images.

## 🏗️ Architecture 🏗️

The application is composed of the following main components:

- `app.py`: The main Streamlit application file that handles the user interface and user interactions.
- `game_manager.py`: An in-memory game manager that handles the game logic, including creating and managing rooms, players, rounds, and scoring.
- `groq_client.py`: A client for interacting with the Groq and Unsplash APIs to fetch item data.
- `.env`: A file for storing environment variables, such as API keys.

## 🚀 Getting Started 🚀

### ✅ Prerequisites

- Python 3.7+
- An Unsplash API key
- A Groq API key

### 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/guess-the-price-game.git
    cd guess-the-price-game
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

### ⚙️ Configuration

1.  **Create a `.env` file:**

    Create a `.env` file in the root of the project by copying the `.env.example` file:

    ```bash
    cp .env.example .env
    ```

2.  **Add your API keys to the `.env` file:**

    ```
    UNSPLASH_API_KEY="YOUR_UNSPLASH_API_KEY"
    GROQ_API_URL="YOUR_GROQ_API_URL"
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    ```

### ▶️ Running the Application

```bash
streamlit run app.py
```

## ☁️ Deployment ☁️

This app can be easily deployed to Streamlit Cloud.

1.  **Push your code to a GitHub repository.**
2.  **Go to the Streamlit Cloud dashboard and create a new app.**
3.  **Connect your GitHub repository and select the `main` branch.**
4.  **Set the environment variables in the advanced settings.**
5.  **Deploy the app!**

## 📝 Notes 📝

- This implementation stores all game state in-memory. For a production deployment, you should use a database like Redis so that multiple app instances can share state.
- The app uses the Unsplash API to fetch random images of items. You will need to create a free developer account to get an API key.
- The app uses the Groq API to generate a realistic price for the items. You will need to create a free account to get an API key.
