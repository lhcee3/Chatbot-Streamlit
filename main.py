import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title(" Shortspin Chatbot")
st.write("Ask me anything! I'm powered by Google's Gemini Pro Model. Built by [Aneesh](https://github.com/lhcee3)")

api_key_input = st.text_input("Enter your Google Gemini API Key:", type="password", key="gemini_api_key_input")

if api_key_input:
    genai.configure(api_key=api_key_input)
    
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except Exception as e:
        st.error(f"Could not list available Gemini models. Please check your API key and network connection. Error: {e}")
        st.stop()

    MODEL_TO_USE = "models/gemini-1.5-flash" 
    
    if MODEL_TO_USE not in available_models:
        st.warning(
            f"The preferred model `{MODEL_TO_USE}` is not directly available for `generateContent` "
            f"in your region/project. Available models are: {', '.join(available_models)}. "
            "Attempting to find a suitable alternative."
        )
        if "models/gemini-2.0-flash" in available_models:
            MODEL_TO_USE = "models/gemini-2.0-flash"
            st.info(f"Falling back to `{MODEL_TO_USE}`.")
        elif "models/gemini-1.5-flash-latest" in available_models:
            MODEL_TO_USE = "models/gemini-1.5-flash-latest"
            st.info(f"Falling back to `{MODEL_TO_USE}`.")
        elif "models/gemini-pro" in available_models:
            MODEL_TO_USE = "models/gemini-pro"
            st.info(f"Falling back to `{MODEL_TO_USE}`.")
        elif available_models:
            MODEL_TO_USE = available_models[0] 
            st.info(f"Falling back to first available model: `{MODEL_TO_USE}`.")
        else:
            st.error("No suitable models found that support `generateContent`. Please check your API key and Google Cloud project settings.")
            st.stop()

    try:
        model = genai.GenerativeModel(MODEL_TO_USE)
        st.success("Ready to chat!") 
    except Exception as e:
        st.error(f"Error initializing Gemini model '{MODEL_TO_USE}'. Please check your API key or try another model. Details: {e}")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat = model.start_chat(history=[])

    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(text)

    user_query = st.chat_input("Your message:")

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)
        
        st.session_state.chat_history.append(("user", user_query))

        try:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                response = st.session_state.chat.send_message(user_query, stream=True)
                
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

            st.session_state.chat_history.append(("assistant", full_response))

        except Exception as e:
            st.error(f"An error occurred while getting a response from Gemini: {e}")
            st.session_state.chat_history.append(("assistant", f"Error: {e}"))
            with st.chat_message("assistant"):
                st.error("I'm sorry, I couldn't process that request.")

else:
    st.info("Please enter your Google Gemini API Key to start chatting Find it [here](https://aistudio.google.com/apikey).")
