import streamlit as st 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import yaml
import os

# Initialize session state for managing multiple chat histories
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}
if 'active_chat' not in st.session_state:
    st.session_state.active_chat = None
if 'chat_titles' not in st.session_state:
    st.session_state.chat_titles = {}  # Store titles based on conversation content

# Function to create a new chat session
def start_new_chat():
    new_chat_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
    st.session_state.chat_sessions[new_chat_id] = []
    st.session_state.chat_titles[new_chat_id] = "Untitled Chat"
    st.session_state.active_chat = new_chat_id

# Function to switch between chat sessions
def switch_chat(session_id):
    st.session_state.active_chat = session_id

# Function to dynamically name the chat based on conversation content
def update_chat_title(chat_id, user_input):
    # Simple approach: use the first few words of the conversation as the chat title
    if len(user_input) > 35:
        title = user_input[:35] + "..."
    else:
        title = user_input
    st.session_state.chat_titles[chat_id] = title

# Sidebar layout
with st.sidebar:
    

    # Start New Chat Button at the Top of the Sidebar
    if st.button('Start New Chat'):
        start_new_chat()

    
    
    # Sidebar for Role and Model Selection
    ROLE = st.selectbox("SELECT ROLE:", ("General Purpose", "Healthcare", "Finance", "Education"))
    ANSWER = st.radio("SELECT ANSWER LENGHT:", ('Detailed', 'Precise'))


    # Display chat session titles in a column list, only if there are sessions
    st.markdown("### ---------------- Chat history ----------------")  
    if st.session_state.chat_sessions:
        for chat_id, chat_title in st.session_state.chat_titles.items():
            if st.button(chat_title):
                switch_chat(chat_id)

    

# Load configuration for the chatbot model
def Chat_bot():
    # Title and logo
    col1, col2 = st.columns([1, 1], vertical_alignment="center")
    col1.title("Chatbot :")
    col2.image("chatbot.png", width=50)

    # Load the configuration file
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)

    # Set Google API key
    os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]
    
    # Initialize the Google Generative AI model
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        convert_system_message_to_human=True
    )

    # CSS for ChatGPT-like conversation style
    st.markdown(
        """
        <style>
        .message {
            margin-bottom: 10px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        .user-message, .bot-message {
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
            font-size: 16px;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            margin-top: 15px;
            background-color: #f1f0f0;
            color: black;
            text-align: left;
            margin-bottom: 15px;
        }
        .bot-avatar {
            margin-top: 15px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
            margin-right: 10px;
        }
        .bot-container {
            display: flex;
            align-items: top;
            gap: 10px;
        }
        .user-container {
            display: flex;
            justify-content: flex-end;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # If no active chat exists, create a default chat session for the first interaction
    if st.session_state.active_chat is None:
        if not st.session_state.chat_sessions:
            start_new_chat()
        else:
            st.session_state.active_chat = list(st.session_state.chat_sessions.keys())[0]

    # Fetch current chat session
    conversation_history = st.session_state.chat_sessions[st.session_state.active_chat]

    # Handle chat input
    prompt = st.chat_input("Say something", key="unique_chat_input_key")
    if prompt:
        # Define role-based system messages
        role_prompts = {
            "General Purpose": f"You are a general-purpose assistant. Provide clear, {ANSWER}, and helpful responses.",
            "Healthcare": f"You are a healthcare assistant if asked something irrelevent dont answer it just say i dont know. Provide medically accurate and {ANSWER} responses.",
            "Finance": f"You are a financial assistant if asked something irrelevent dont answer it just say i dont know. Provide accurate and {ANSWER} financial advice.",
            "Education": f"You are an education assistant if asked something irrelevent dont answer it just say i dont know. Provide {ANSWER} and informative responses to support learning."
        }

        # Prepare messages for the AI model based on role
        system_message = role_prompts.get(ROLE, "Provide clear and helpful responses.")
        message_list = [HumanMessage(content=system_message)]

        # Add conversation history from the active chat session
        for item in conversation_history:
            message_list.append(HumanMessage(content=item['input']))
            message_list.append(HumanMessage(content=item['response']))

        message_list.append(HumanMessage(content=prompt))

        # Get AI response
        ai_msg = llm.invoke(message_list)

        # Append the current conversation to the active chat session
        response_content = ai_msg.content.strip()
        conversation_history.append({
            'input': prompt,
            'response': response_content,
            'sender': 'user'
        })

        # Update the title of the chat based on the first user input
        if len(conversation_history) == 1:  # Title the chat only based on the first message
            update_chat_title(st.session_state.active_chat, prompt)

    # Display the conversation history of the current chat
    with st.container():
        if conversation_history:
            for item in conversation_history:
                # User's message
                st.markdown(f'''
                <div class="user-container">
                    <div class="user-message">{item["input"]}</div>
                </div>
                ''', unsafe_allow_html=True)

                # Bot's response with bot avatar
                st.markdown(f'''
                <div class="bot-container">
                    <img src="https://img.freepik.com/free-vector/cartoon-style-robot-vectorart_78370-4103.jpg?w=740&t=st=1726496426~exp=1726497026~hmac=a0a105a9b0d48986bf0c79465a47bb245fbd942a31022029288d102531e47e40" class="bot-avatar"/>  <!-- Bot's avatar here -->
                    <div class="bot-message">{item["response"]}</div>
                </div>
                ''', unsafe_allow_html=True)

Chat_bot()
