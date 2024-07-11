SailBuddy is an interactive chatbot application designed to recommend songs and videos from Spotify and YouTube based on user queries. The goal is to provide users with mood-enhancing recommendations using the power of AI and various APIs.

Features
Spotify Integration: Get personalized song recommendations from your Spotify library.
YouTube Integration: Get relevant video suggestions from YouTube to improve your mood.
Conversational AI: Interact with the chatbot for a seamless experience.
Customizable UI: Modern and sleek user interface built with Streamlit.

Installation
Prerequisites

Ensure you have Python 3.7+ installed on your machine. You will also need to install the necessary libraries listed in the requirements.txt file.

Install Dependencies
You can install the required dependencies using pip:

pip install -r requirements.txt

Set Up Environment Variables
Create a .env file in the root directory of the project and add the following environment variables:

SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=your_spotify_redirect_uri
OPENAI_API_KEY=your_openai_api_key
Replace your_spotify_client_id, your_spotify_client_secret, your_spotify_redirect_uri, and your_openai_api_key with your actual credentials.

Usage
Run the application using the following command:
streamlit run final.py
This will start the Streamlit application, and you can access it in your web browser at http://localhost:8501.

Interacting with SailBuddy
Enter your query in the input box (e.g., "Suggest some happy songs from my Spotify library" or "Recommend some motivational YouTube videos").
Click on the "Submit Query" button.
View the recommended songs and videos displayed on the page.

Customization
The UI is styled using custom CSS. You can modify the appearance by editing the CSS section in final.py.
