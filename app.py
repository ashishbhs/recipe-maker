import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini Pro API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini Pro Model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to get recipe details from Gemini API
def get_recipe_details(query):
    question = f"Can you suggest a detailed recipe based on these ingredients: {query}? Or a specific recipe for {query} with over 500 words."
    response = chat.send_message(question, stream=True)
    return response

# Function to ensure response has at least 500 words
def ensure_minimum_words(text, min_words=500):
    words = text.split()
    if len(words) >= min_words:
        return text  # If already sufficient, return the text as is.
    
    return text + " Please provide more details on preparation steps, cooking tips, or variations for the recipe."

# Function to format the response dynamically for recipes
def format_recipe_response(text):
    formatted_text = text

    # Step 1: Replace headings like "*Ingredients:*" and "*Instructions:*" with Markdown headers
    formatted_text = re.sub(r'\*(Ingredients|Instructions)\:\*', r'### \1:', formatted_text)
    
    # Step 2: Convert steps or ingredients into bullet points
    formatted_text = re.sub(r'\*(.*?)\*\:', r'- **\1:**', formatted_text)

    # Step 3: Ensure bullet points for lists
    lines = formatted_text.split('\n')
    formatted_lines = []
    for line in lines:
        if re.match(r'^\d+\.', line.strip()):  # Handling steps like '1.' or '2.'
            formatted_lines.append(f"- {line.strip()}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

# Streamlit app setup
st.set_page_config(page_title="Recipe Maker App", layout="wide")
st.title("🍽️ Recipe Maker App ✨")
st.write("**Welcome to the Recipe Maker App!**")
st.write("Enter the ingredients or dish name in the input box below, and we'll suggest a delicious recipe tailored just for you!")

# User input and submission
recipe_query = st.text_input("🔍 Enter ingredients or dish name (e.g., chicken, pasta, chocolate cake, etc.):")
submit_button = st.button("🧑‍🍳 Get Recipe")

if submit_button and recipe_query:
    # Clear chat history on new search
    st.session_state['chat_history'] = []

    # Get recipe details from Gemini API
    with st.spinner("Fetching your recipe..."):
        response = get_recipe_details(recipe_query)
        response_text = ""

        for chunk in response:
            response_text += chunk.text

        # Ensure the response is more than 500 words
        expanded_response = ensure_minimum_words(response_text)

        # Format the response for recipe display
        formatted_response = format_recipe_response(expanded_response)

        # Update chat history
        st.session_state['chat_history'].append(("You", recipe_query))
        st.session_state['chat_history'].append(("Gemini", formatted_response))

        st.success("Recipe fetched successfully! 🎉")

# Display chat history
st.subheader("🥘 Your Recipe")
if 'chat_history' in st.session_state:
    for role, message in st.session_state['chat_history']:
        st.write(f"**{role}:**")
        st.markdown(message)  # Using markdown to show formatted recipe

# Footer
st.markdown("---")
st.write("🔗 For more culinary adventures, visit our [website](#)!")
