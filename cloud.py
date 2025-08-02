  
import os
import os
# For Streamlit Cloud: Do NOT force duckdb backend, let CHROMA_DB_IMPL be set by environment variable.
# To use ChromaDB on Streamlit Cloud, set CHROMA_DB_IMPL=postgres and provide PostgreSQL credentials in app secrets or environment variables.
os.environ["CHROMA_DB_IMPL"] = os.getenv("CHROMA_DB_IMPL", "duckdb")  # Default to duckdb if not set
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# Fetch API keys from Streamlit secrets (for Streamlit Cloud) or environment (for local dev)
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

serper_api_key = get_secret("SERPER_API_KEY")
openai_api_key = get_secret("OPENAI_API_KEY")
if serper_api_key:
    os.environ["SERPER_API_KEY"] = serper_api_key
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

# Initialize the search tool
search_tool = SerperDevTool()

def get_llm():
    return LLM(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.01,  # Very low temperature for highly deterministic, cost-effective responses
        verbose=True
    )

def create_agents():
    """Create the specialized nutrition agents."""
    llm = get_llm()
    
    # Nutrition Researcher
    nutritionist = Agent(
        role='Nutrition Specialist',
        goal='Research and develop personalized nutritional recommendations based on scientific evidence',
        backstory='''You are a highly qualified nutritionist with expertise in therapeutic diets, 
                    nutrient interactions, and dietary requirements across different health conditions. 
                    Your recommendations are always backed by peer-reviewed research.''',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    # Medical Nutrition Specialist
    medical_specialist = Agent(
        role='Medical Nutrition Therapist',
        goal='Analyze medical conditions and provide appropriate dietary modifications',
        backstory='''With dual training in medicine and nutrition, you specialize in managing 
                    nutrition-related aspects of various medical conditions. You understand 
                    medication-food interactions and how to optimize nutrition within medical constraints.''',
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    # Diet Plan Creator
    diet_planner = Agent(
        role='Therapeutic Diet Planner',
        goal='Create detailed, practical and enjoyable meal plans tailored to individual needs',
        backstory='''You excel at transforming clinical nutrition requirements into delicious, 
                    practical eating plans. You have extensive knowledge of food preparation, 
                    nutrient preservation, and food combinations that optimize both health and enjoyment.''',
        llm=llm,
        verbose=True
    )
    
    return nutritionist, medical_specialist, diet_planner

def create_tasks(nutritionist, medical_specialist, diet_planner, user_info):
    """Create tasks for each agent based on user information."""
    
    # First task: Research nutrition needs based on demographics
    demographics_research = Task(
        description=f'''Research nutritional needs for an individual with the following demographics:
            - Age: {user_info['age']}
            - Gender: {user_info['gender']}
            - Height: {user_info['height']}
            - Weight: {user_info['weight']}
            - Activity Level: {user_info['activity_level']}
            - Goals: {user_info['goals']}
            
            Provide detailed nutritional requirements including:
            1. Caloric needs (basal and adjusted for activity)
            2. Macronutrient distribution (proteins, carbs, fats)
            3. Key micronutrients particularly important for this demographic
            4. Hydration requirements
            5. Meal timing and frequency recommendations''',
        agent=nutritionist,
        expected_output="A comprehensive nutritional profile with scientific rationale"
    )
    
    # Second task: Analyze medical conditions and adjust nutritional recommendations
    medical_analysis = Task(
        description=f'''Analyze the following medical conditions and medications, then provide dietary modifications:
            - Medical Conditions: {user_info['medical_conditions']}
            - Medications: {user_info['medications']}
            - Allergies/Intolerances: {user_info['allergies']}
            
            Consider the baseline nutritional profile and provide:
            1. Specific nutrients to increase or limit based on each condition
            2. Food-medication interactions to avoid
            3. Potential nutrient deficiencies associated with these conditions/medications
            4. Foods that may help manage symptoms or improve outcomes
            5. Foods to strictly avoid''',
        agent=medical_specialist,
        context=[demographics_research],
        expected_output="A detailed analysis of medical nutrition therapy adjustments"
    )
    
    # Third task: Create the comprehensive diet plan
    diet_plan = Task(
        description=f'''Create a detailed, practical diet plan incorporating all information:
            - User's Food Preferences: {user_info['food_preferences']}
            - Cooking Skills/Time: {user_info['cooking_ability']}
            - Budget Constraints: {user_info['budget']}
            - Cultural/Religious Factors: {user_info['cultural_factors']}
            
            Develop a comprehensive nutrition plan that includes:
            1. Specific foods to eat daily, weekly, and occasionally with portion sizes
            2. A 7-day meal plan with specific meals and recipes
            3. Grocery shopping list with specific items
            4. Meal preparation tips and simple recipes
            5. Eating out guidelines and suggested restaurant options/orders
            6. Supplement recommendations if necessary (with scientific justification)
            7. Hydration schedule and recommended beverages
            8. How to monitor progress and potential adjustments over time''',
        agent=diet_planner,
        context=[demographics_research, medical_analysis],
        expected_output="A comprehensive, practical, and personalized nutrition plan"
    )
    
    return [demographics_research, medical_analysis, diet_plan]

def create_crew(agents, tasks):
    """Create the CrewAI crew with the specified agents and tasks."""
    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=True
    )

def run_nutrition_advisor(user_info):
    """Run the nutrition advisor with the user information."""
    try:
        # Create agents
        nutritionist, medical_specialist, diet_planner = create_agents()
        
        # Create tasks
        tasks = create_tasks(nutritionist, medical_specialist, diet_planner, user_info)
        
        # Create crew
        crew = create_crew([nutritionist, medical_specialist, diet_planner], tasks)
        
        # Execute the crew
        with st.spinner('Our nutrition team is creating your personalized plan. This may take a few minutes...'):
            result = crew.kickoff()
        
        return result
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def app():
    import base64
    # --- Sidebar Logo with Unique Style and Animation ---
    logo_path = os.path.join(os.path.dirname(__file__), "Logo.png")
    ai_logo_path = os.path.join(os.path.dirname(__file__), "AI.png")
    encoded_logo = None
    encoded_ai_logo = None
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
    if os.path.exists(ai_logo_path):
        with open(ai_logo_path, "rb") as image_file:
            encoded_ai_logo = base64.b64encode(image_file.read()).decode()

    with st.sidebar:
        # Logo and animated style
        if encoded_logo:
            st.markdown(
                f"""
                <style>
                @keyframes colorfulGlow {{
                    0% {{ box-shadow: 0 0 24px #ffd200, 0 0 0px #00c6ff; filter: hue-rotate(0deg); }}
                    25% {{ box-shadow: 0 0 32px #00c6ff, 0 0 12px #f7971e; filter: hue-rotate(90deg); }}
                    50% {{ box-shadow: 0 0 40px #f7971e, 0 0 24px #ffd200; filter: hue-rotate(180deg); }}
                    75% {{ box-shadow: 0 0 32px #00c6ff, 0 0 12px #ffd200; filter: hue-rotate(270deg); }}
                    100% {{ box-shadow: 0 0 24px #ffd200, 0 0 0px #00c6ff; filter: hue-rotate(360deg); }}
                }}
                .colorful-animated-logo {{
                    animation: colorfulGlow 2.5s linear infinite;
                    transition: box-shadow 0.3s, filter 0.3s;
                    border-radius: 30%;
                    box-shadow: 0 2px 12px #00c6ff;
                    border: 2px solid #ffd200;
                    background: #232526;
                    object-fit: cover;
                }}
                .sidebar-logo {{
                    text-align: center;
                    margin-bottom: 12px;
                }}
                </style>
                <div class='sidebar-logo'>
                    <img class='colorful-animated-logo' src='data:image/png;base64,{encoded_logo}' alt='Logo' style='width:150px;height:150px;'>
                    <div style='color:#00c6ff;font-size:1.1em;font-family:sans-serif;font-weight:bold;text-shadow:0 1px 6px #ffd200;margin-top:8px;'>SehaatSaathi.AI🧑‍⚕️</div>
                </div>
                <!-- Second logo below the first -->
                <div class='sidebar-AI' style='margin-top:0;'>
                    {f"<img src='data:image/png;base64,{encoded_ai_logo}' alt='AI' style='width:210px;height:220px;border-radius:30%;box-shadow:0 2px 12px #00c6ff;border:2px solid #ffd200;margin-bottom:8px;background:#232526;object-fit:cover;'>" if encoded_ai_logo else "<div style='color:#ff4b4b;'>AI.png not found</div>"}
                    <div style='color:#00c6ff;font-size:1.1em;font-family:sans-serif;font-weight:bold;text-shadow:0 1px 6px #ffd200;margin-top:8px;'></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Developer info and image below the logos
            st.markdown("<div style='text-align:center;font-size:1.1em;margin-top:10px;'>👨👨‍💻<b>Developer:</b> <br>Abhishek💖Yadav</br></div>", unsafe_allow_html=True)
            developer_path = os.path.join(os.path.dirname(__file__), "pic.jpg")
            if os.path.exists(developer_path):
                st.image(developer_path, caption="Abhishek Yadav", use_container_width=True)
            else:
                st.warning("pic.jpg file not found. Please check the file path.")
        else:
            st.markdown(
                "<div style='text-align:center;font-size:2em;margin:16px 0;'>🚀</div><div style='text-align:center;color:#00c6ff;font-weight:bold;'>NewsCraft.AI</div>",
                unsafe_allow_html=True
            )
    # Main Streamlit application (docstring removed to prevent display)
    st.set_page_config(page_title="SehaatSaathi.AI", page_icon="🥗", layout="wide")


    # --- New Modern Glassmorphism & Teal/Purple/Orange UI CSS ---
    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            background: linear-gradient(135deg, #181d27 0%, #1e2746 100%) !important;
            color: #f7f7fa !important;
        }
        .stApp {
            background: linear-gradient(135deg, #181d27 0%, #1e2746 100%) !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(30,39,70,0.7);
            border-radius: 16px;
            padding: 0.3em 0.7em;
            box-shadow: 0 4px 24px 0 rgba(34,211,238,0.08);
            backdrop-filter: blur(8px);
        }
        .stTabs [data-baseweb="tab"] {
            color: #f7f7fa;
            font-weight: 700;
            font-size: 1.13em;
            border-radius: 10px 10px 0 0;
            margin: 0 0.25em;
            background: rgba(30,39,70,0.5);
            transition: background 0.3s, color 0.3s;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #22d3ee 0%, #a78bfa 60%, #fb923c 100%);
            color: #fff;
            box-shadow: 0 2px 16px 0 #22d3ee33;
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea, .stNumberInput>div>input, .stSelectbox>div>div>div>div, .stMultiSelect>div>div>div>div, .stSlider>div>div>div>input {
            background: rgba(30,39,70,0.7) !important;
            color: #f7f7fa !important;
            border: 1.5px solid #22d3ee !important;
            border-radius: 10px !important;
        }
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(90deg, #22d3ee 0%, #a78bfa 60%, #fb923c 100%);
            color: #fff;
            border: none;
            border-radius: 12px;
            font-weight: bold;
            font-size: 1.13em;
            padding: 0.7em 1.7em;
            margin: 0.25em 0;
            box-shadow: 0 2px 16px 0 #a78bfa33;
            transition: transform 0.18s, box-shadow 0.18s, background 0.3s;
            cursor: pointer;
            outline: none;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            transform: scale(1.07) translateY(-2px);
            box-shadow: 0 8px 32px 0 #22d3ee33;
            background: linear-gradient(90deg, #fb923c 0%, #a78bfa 60%, #22d3ee 100%);
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>textarea:focus {
            border: 2px solid #a78bfa !important;
            box-shadow: 0 0 0 2px #a78bfa33 !important;
        }
        .stSelectbox>div>div>div>div:focus, .stMultiSelect>div>div>div>div:focus {
            border: 2px solid #fb923c !important;
            box-shadow: 0 0 0 2px #fb923c33 !important;
        }
        .stSlider>div>div>div>input:focus {
            border: 2px solid #22d3ee !important;
            box-shadow: 0 0 0 2px #22d3ee33 !important;
        }
        .stAlert, .stInfo, .stWarning, .stSuccess {
            background: rgba(30,39,70,0.7) !important;
            color: #f7f7fa !important;
            border-left: 6px solid #fb923c !important;
            border-radius: 10px !important;
        }
        .stDataFrame, .stTable {
            background: rgba(30,39,70,0.7) !important;
            color: #f7f7fa !important;
            border-radius: 12px !important;
        }
        .stMarkdown, .stHeader, .stSubheader, .stTitle {
            color: #22d3ee !important;
        }
        /* Chat bubbles glassmorphism */
        .chat-container {
            background: rgba(30,39,70,0.7) !important;
            border: 1.5px solid #a78bfa !important;
            box-shadow: 0 2px 16px 0 #22d3ee22;
            backdrop-filter: blur(6px);
        }
        .chat-bubble-user {
            background: linear-gradient(90deg, #22d3ee 0%, #a78bfa 100%) !important;
            color: #fff !important;
            box-shadow: 0 2px 8px 0 #22d3ee33;
        }
        .chat-bubble-ai {
            background: linear-gradient(90deg, #fb923c 0%, #a78bfa 100%) !important;
            color: #fff !important;
            box-shadow: 0 2px 8px 0 #a78bfa33;
        }
        /* Animate send button */
        .stButton>button[key="send_chat"] {
            animation: pulse2 1.3s infinite alternate;
        }
        @keyframes pulse2 {
            0% { box-shadow: 0 0 0 0 #22d3ee55; }
            100% { box-shadow: 0 0 0 12px #a78bfa22; }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1em; margin-bottom: 0.5em;">
        <span style="font-size:2.5em;">🥗</span>
        <span style="font-size:2.1em; font-weight: bold; background: linear-gradient(90deg, #22d3ee 0%, #a78bfa 60%, #fb923c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SehaatSaathi.AI</span>
    </div>
    <div style="font-size:1.2em; color:#f7f7fa; margin-bottom:1.5em;">AI-Powered Digital Nutrition, Personalized for You</div>
    """, unsafe_allow_html=True)
    
    # Create tabs for organization (add chatbot as tab2)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Basic Information", "AI Support Assistant Chatbot", "Health Details", "Preferences & Lifestyle", "Analytics & Customization"
    ])

    # --- AI Support Assistant Chatbot Tab ---
    with tab2:
        st.header("🤖 AI Support Assistant Chatbot")
        st.write("Chat one-to-one with your AI assistant. Your conversation is remembered!")
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        # --- Enhanced Chat UI ---
        st.markdown("""
            <style>
            .chat-container {max-height: 400px; overflow-y: auto; padding: 0.5em 0; border-radius: 8px; background: #f7f7fa; border: 1px solid #e0e0e0; margin-bottom: 1em;}
            .chat-bubble-user {background: #d1e7ff; color: #222; padding: 0.7em 1em; border-radius: 18px 18px 4px 18px; margin: 0.3em 0 0.3em 2em; display: inline-block; max-width: 80%;}
            .chat-bubble-ai {background: #f0f0f0; color: #222; padding: 0.7em 1em; border-radius: 18px 18px 18px 4px; margin: 0.3em 2em 0.3em 0; display: inline-block; max-width: 80%;}
            .chat-row {display: flex; align-items: flex-end;}
            .chat-avatar {width: 32px; height: 32px; border-radius: 50%; margin: 0 0.5em;}
            .chat-row.user {justify-content: flex-end;}
            .chat-row.ai {justify-content: flex-start;}
            </style>
        """, unsafe_allow_html=True)
        # Scrollable chat area
        chat_html = ["<div class='chat-container'>"]
        for entry in st.session_state['chat_history']:
            if entry['role'] == 'user':
                chat_html.append(f"<div class='chat-row user'><div class='chat-bubble-user'>{entry['content']}</div><img class='chat-avatar' src='https://cdn-icons-png.flaticon.com/512/1946/1946429.png' alt='User'></div>")
            else:
                chat_html.append(f"<div class='chat-row ai'><img class='chat-avatar' src='https://cdn-icons-png.flaticon.com/512/4712/4712035.png' alt='AI'><div class='chat-bubble-ai'>{entry['content']}</div></div>")
        chat_html.append("</div>")
        st.markdown("\n".join(chat_html), unsafe_allow_html=True)
        # Input area with send button on same line
        col1, col2 = st.columns([8,1])
        with col1:
            user_message = st.text_area("Type your message...", key="chat_input", height=68, label_visibility="collapsed")
        with col2:
            send_clicked = st.button("➡️", key="send_chat", help="Send message")
        # Clear chat button
        if st.button("🧹 Clear Chat", key="clear_chat"):
            st.session_state['chat_history'] = []
            st.rerun()
        # Handle sending
        if send_clicked:
            if user_message.strip():
                st.session_state['chat_history'].append({'role': 'user', 'content': user_message})
                # Build conversation for context
                conversation = "\n".join([f"User: {e['content']}" if e['role']=='user' else f"AI: {e['content']}" for e in st.session_state['chat_history']])
                with st.spinner("AI is typing..."):
                    # Use ChatOpenAI directly for chatbot responses
                    try:
                        chat_llm = ChatOpenAI(
                            model="gpt-3.5-turbo",
                            openai_api_key=os.getenv("OPENAI_API_KEY"),
                            temperature=0.01,
                        )
                        from langchain.schema import HumanMessage, SystemMessage
                        messages = [
                            SystemMessage(content="You are a helpful nutrition and health assistant. Continue this conversation."),
                        ]
                        # Add conversation history
                        for e in st.session_state['chat_history']:
                            if e['role'] == 'user':
                                messages.append(HumanMessage(content=e['content']))
                            else:
                                messages.append(SystemMessage(content=e['content']))
                        ai_response = chat_llm(messages).content
                    except Exception as e:
                        ai_response = f"Sorry, AI response is not available. ({e})"
                st.session_state['chat_history'].append({'role': 'ai', 'content': str(ai_response)})
                st.rerun()

    # --- Existing Tabs ---
    with tab1:
        st.header("Personal Information")
        col1, col2 = st.columns(2)
        # --- AI Auto Suggestion Button ---
        if 'auto_suggested' not in st.session_state:
            st.session_state['auto_suggested'] = False
        if st.button("AI Auto-Fill My Info"):
            # Mock AI suggestions (replace with real LLM call for production)
            st.session_state['age'] = 28
            st.session_state['gender'] = "Male"
            st.session_state['height'] = "5'9\""
            st.session_state['weight'] = "155 lbs"
            st.session_state['activity_level'] = "Moderately Active"
            st.session_state['goals'] = ["Muscle Building", "Better Energy"]
            st.session_state['auto_suggested'] = True
        # Use session_state for auto-suggested or user input
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.get('age', 30), key="age")
            gender = st.selectbox("Gender", ["Male", "Female", "Non-binary/Other"], index=["Male", "Female", "Non-binary/Other"].index(st.session_state.get('gender', "Male")), key="gender")
            height = st.text_input("Height (e.g., 5'10\" or 178 cm)", st.session_state.get('height', "5'10\""), key="height")
        with col2:
            weight = st.text_input("Weight (e.g., 160 lbs or 73 kg)", st.session_state.get('weight', "160 lbs"), key="weight")
            activity_level = st.select_slider(
                "Activity Level",
                options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                value=st.session_state.get('activity_level', "Sedentary"),
                key="activity_level"
            )
            goals = st.multiselect(
                "Nutrition Goals (AI suggestions: Muscle Building, Better Energy)",
                ["Weight Loss", "Weight Gain", "Maintenance", "Muscle Building", "Better Energy", 
                 "Improved Athletic Performance", "Disease Management", "General Health"],
                default=st.session_state.get('goals', []),
                key="goals"
            )

    with tab2:
        st.header("Health Information")
        # AI suggestions for health info
        if st.button("AI Suggest Health Info"):
            st.session_state['medical_conditions'] = "None"
            st.session_state['medications'] = "None"
            st.session_state['allergies'] = "Lactose"
        medical_conditions = st.text_area(
            "Medical Conditions (separate with commas)",
            value=st.session_state.get('medical_conditions', ""),
            placeholder="E.g., Diabetes Type 2, Hypertension, Hypothyroidism...",
            key="medical_conditions"
        )
        medications = st.text_area(
            "Current Medications (separate with commas)",
            value=st.session_state.get('medications', ""),
            placeholder="E.g., Metformin, Lisinopril, Levothyroxine...",
            key="medications"
        )
        allergies = st.text_area(
            "Food Allergies/Intolerances (separate with commas)",
            value=st.session_state.get('allergies', ""),
            placeholder="E.g., Lactose, Gluten, Shellfish, Peanuts...",
            key="allergies"
        )

    with tab3:
        st.header("Preferences & Lifestyle")
        col1, col2 = st.columns(2)
        # AI suggestions for preferences
        if st.button("AI Suggest Preferences"):
            st.session_state['food_preferences'] = "Prefer plant-based, dislike seafood"
            st.session_state['lock_foods'] = "Oats, Broccoli"
            st.session_state['cooking_ability'] = "Average"
            st.session_state['budget'] = "Moderate"
            st.session_state['exclude_foods'] = "Fish, Peanuts"
            st.session_state['cultural_factors'] = "No specific factors"
        with col1:
            food_preferences = st.text_area(
                "Food Preferences & Dislikes",
                value=st.session_state.get('food_preferences', ""),
                placeholder="E.g., Prefer plant-based, dislike seafood...",
                key="food_preferences"
            )
            # New: Lock favorite foods
            lock_foods = st.text_area(
                "Lock Favorite Foods (comma separated)",
                value=st.session_state.get('lock_foods', ""),
                placeholder="E.g., Oats, Chicken, Broccoli",
                key="lock_foods"
            )
            cooking_ability = st.select_slider(
                "Cooking Skills & Available Time",
                options=["Very Limited", "Basic/Quick Meals", "Average", "Advanced/Can Spend Time", "Professional Level"],
                value=st.session_state.get('cooking_ability', "Average"),
                key="cooking_ability"
            )
        with col2:
            budget = st.select_slider(
                "Budget Considerations",
                options=["Very Limited", "Budget Conscious", "Moderate", "Flexible", "No Constraints"],
                value=st.session_state.get('budget', "Moderate"),
                key="budget"
            )
            # New: Exclude disliked foods
            exclude_foods = st.text_area(
                "Exclude Disliked Foods (comma separated)",
                value=st.session_state.get('exclude_foods', ""),
                placeholder="E.g., Tofu, Fish, Peanuts",
                key="exclude_foods"
            )
            cultural_factors = st.text_area(
                "Cultural or Religious Dietary Factors",
                value=st.session_state.get('cultural_factors', ""),
                placeholder="E.g., Halal, Kosher, Mediterranean tradition...",
                key="cultural_factors"
            )

    # New: Analytics & Customization Tab
    with tab4:
        st.header("Analytics & Customization")
        st.info("After generating your plan, you will see nutrition analytics and can swap meals here.")
        # Placeholder for charts and meal plan table
        if 'meal_plan_df' in st.session_state:
            st.subheader("7-Day Meal Plan Table")
            st.dataframe(st.session_state['meal_plan_df'])
            st.subheader("Macronutrient Breakdown")
            st.bar_chart(st.session_state['macro_data'])
            st.subheader("Hydration Schedule")
            st.line_chart(st.session_state['hydration_data'])
            # Interactive swap (mock)
            st.write("Swap a meal by selecting a row and entering a new meal below:")
            swap_idx = st.number_input("Row to swap (0-based)", min_value=0, max_value=len(st.session_state['meal_plan_df'])-1, value=0)
            new_meal = st.text_input("New meal name")
            if st.button("Swap Meal"):
                st.session_state['meal_plan_df'].iloc[swap_idx, 1] = new_meal
                st.success(f"Meal at row {swap_idx} swapped!")
        else:
            st.warning("Generate a plan to see analytics and customization options.")
    
    # Collect all user information
    user_info = {
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "activity_level": activity_level,
        "goals": ", ".join(goals) if goals else "General health improvement",
        "medical_conditions": medical_conditions or "None reported",
        "medications": medications or "None reported",
        "allergies": allergies or "None reported",
        "food_preferences": food_preferences or "No specific preferences",
        "cooking_ability": cooking_ability,
        "budget": budget,
        "cultural_factors": cultural_factors or "No specific factors",
        # New fields for customization
        "lock_foods": lock_foods or "",
        "exclude_foods": exclude_foods or ""
    }
    
    # Check if API keys are present
    if not os.getenv("SERPER_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ API keys not detected. Please add your SERPER_API_KEY and OPENAI_API_KEY to your .env file.")
    
    # Create a submission button
    if st.button("Generate Nutrition Plan"):
        if not goals:
            st.error("Please select at least one nutrition goal.")
            return
        # Display user information summary
        with st.expander("Summary of Your Information"):
            st.json(user_info)
        # Run the nutrition advisor
        result = run_nutrition_advisor(user_info)
        if result:
            result_str = str(result)
            st.success("✅ Your personalized nutrition plan is ready!")
            st.markdown("## Your Personalized Nutrition Plan")
            st.markdown(result_str)
            # --- Analytics & Customization Data (Mock for now) ---
            import pandas as pd
            # Mock meal plan table
            meal_plan_data = [
                ["Day 1", "Oats & Berries", 350, 10, 60, 8, 2],
                ["Day 1", "Grilled Chicken Salad", 400, 35, 20, 15, 1],
                ["Day 1", "Veggie Stir Fry", 450, 12, 70, 10, 2],
                ["Day 2", "Egg White Omelette", 300, 25, 5, 10, 1],
                ["Day 2", "Quinoa Bowl", 420, 15, 65, 12, 2],
                ["Day 2", "Salmon & Rice", 500, 30, 50, 20, 2],
            ]
            meal_plan_df = pd.DataFrame(meal_plan_data, columns=["Day", "Meal", "Calories", "Protein", "Carbs", "Fat", "Water(L)"])
            st.session_state['meal_plan_df'] = meal_plan_df
            # Mock macro data
            macro_data = pd.DataFrame({
                "Protein": [120], "Carbs": [270], "Fat": [75]
            })
            st.session_state['macro_data'] = macro_data
            # Mock hydration data
            hydration_data = pd.DataFrame({"Water(L)": [2, 2, 2, 2, 2, 2, 2]}, index=[f"Day {i+1}" for i in range(7)])
            st.session_state['hydration_data'] = hydration_data
            # --- End Analytics & Customization Data ---
            # --- Export Buttons ---
            st.download_button(
                label="Download Nutrition Plan (Markdown)",
                data=result_str,
                file_name="my_nutrition_plan.md",
                mime="text/markdown"
            )
            # PDF Export (mock)
            st.download_button(
                label="Download Nutrition Plan (PDF)",
                data="PDF export coming soon!",
                file_name="my_nutrition_plan.pdf",
                mime="application/pdf"
            )
            # Google Calendar Export (mock)
            st.download_button(
                label="Add Reminders to Google Calendar (.ics)",
                data="ICS export coming soon!",
                file_name="nutrition_reminders.ics",
                mime="text/calendar"
            )
            # Email input for reminders (mock)
            st.text_input("Enter your email for meal/hydration reminders (feature coming soon)")

if __name__ == "__main__":
    app()






