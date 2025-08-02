<img width="1024" height="1024" alt="AI" src="https://github.com/user-attachments/assets/9f4f70ad-6b2b-48fc-baf0-8ec307f4358c" />

<img width="1916" height="1080" alt="app page" src="https://github.com/user-attachments/assets/f524adcf-18f8-4e7e-9fe3-7c24961ccc99" />
OUR APP:-- https://sehaatsaathi-ai-agent.streamlit.app/




# 🥗 SehaatSaathi.AI Agent

> **AI-Powered Digital Nutrition, Personalized for You**  
> Powered By **TECHSEVA SOLUTIONS**

---

## 📝 Introduction

**SehaatSaathi.AI** is a revolutionary **AI-powered digital nutrition assistant** designed to help individuals personalize their health and nutrition journey.  
The app intelligently generates customized nutrition plans based on user input, health data, and preferences.  
With a beautiful modern interface and seamless multi-agent intelligence, SehaatSaathi.AI empowers users to take full control of their wellness with guidance from AI agents acting as digital health coaches.  
This project is fully functional for local or cloud deployment and built for extensibility.  
Whether you're a developer, nutritionist, or enthusiast, this app serves as an excellent foundation for the future of AI-driven personal health.

---

## 🎯 App Purpose

SehaatSaathi.AI acts as a smart virtual nutritionist that personalizes meal plans, calculates hydration needs, and provides suggestions tailored to users' health data and lifestyle factors.  
It uses multiple CrewAI agents to deliver recommendations supported by evidence-based knowledge and real-time AI conversation.

---

## 💎 Key Features

### 🌈 Modern UI & Branding

- **Custom Sidebar**:
  - Animated app logo (`logo.png`)
  - Developer information (`pic.jpg`, Name, Tagline)
  - Clean glassmorphism + gradient-based theme
- **Main Page**:
  - Beautiful, colorful layouts with intuitive interactions
  - Responsive for desktop and mobile screens

---

### 🗂️ Tabbed Interface

#### ✅ 1. Basic Information
- Collects:
  - Age
  - Gender
  - Height
  - Weight
  - Activity level
  - Nutrition goals (muscle gain, weight loss, maintenance)
- AI Auto-Fill button for users needing quick suggestions

#### 💬 2. AI Support Assistant Chatbot
- Interactive real-time chat with the AI nutrition assistant
- Persistent conversation memory
- Powered by OpenAI + LangChain
- Can answer questions, give suggestions, or explain meal plans

#### 🏥 3. Health Details
- Collects sensitive but optional health data:
  - Medical conditions
  - Medications
  - Allergies
- AI helper suggests common health issues to speed up input

#### 🍽️ 4. Preferences & Lifestyle
- Collects:
  - Favorite foods
  - Food dislikes
  - Cooking skills
  - Budget
  - Cultural/religious dietary restrictions
- AI helper can suggest personalized lifestyle or dietary factors

#### 📊 5. Analytics & Customization
- After plan generation:
  - Displays a 7-day meal plan
  - Macronutrient breakdown (protein, carbs, fats)
  - Daily hydration goal and hydration tracker
  - Interactive meal swap system for alternatives

---

### 📝 Personalized Nutrition Plan Generation

When users click **"Generate Nutrition Plan"**:
1. App automatically summarizes all collected user data
2. Launches **CrewAI agents**:
   - **AI Nutritionist** → Analyzes nutrition data and meal structure
   - **Medical Specialist** → Reviews for potential contraindications
   - **Diet Planner** → Creates full 7-day meal plan + hydration
3. Displays customized outputs in easy-to-read cards
4. Provides mock analytics to visualize recommendations

---

### 💾 Download & Export Options

- Download full nutrition plan as **Markdown**
- (Future) Export to **PDF** and **Calendar (.ics)** (currently placeholder)
- Enter email to optionally receive meal plan + reminders later

---

### 🔐 API Key Management

- Securely fetches:
  - `OPENAI_API_KEY`
  - `SERPAPI_KEY`
  - `CREWAI_KEY`  
from **Streamlit secrets** or local **.env file**  
- Supports cloud and local execution

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Main UI |
| CrewAI | Agent orchestration |
| OpenAI | LLM for AI chat and meal planning |
| LangChain | Conversational memory and agent routing |
| Pandas | Data handling + mock analytics |
| Custom CSS | Modern glassmorphism + gradient dark theme |

---

## 🚀 Summary

**SehaatSaathi.AI** is a full-featured, intelligent, interactive AI nutrition assistant.  
It combines rich multi-step user data collection, AI-powered personalization, live chatbot support, downloadable reports, and modern design in a seamless experience.  
This project is production-ready for deployment on **Streamlit Cloud** or any local server and serves as a best-practice template for building **AI-powered wellness agents** using CrewAI and LangGraph.

---

```markdown
## 🌳 LangGraph Decision Tree Workflow

The **SehaatSaathi.AI Agent** app uses a LangGraph-based decision tree to coordinate agent tasks and user interactions.

Below is the complete decision flow for the app from start to end:

```

```
                      ┌─────────────────────┐
                      │    App Launched     │
                      └─────────┬───────────┘
                                │
                ┌───────────────▼────────────────┐
                │ User selects: Start New Session│
                └────────────────┬──────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │    Step 1: Collect Basic Info       │
              │ (age, gender, height, weight, goals)│
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │  Step 2: Collect Health Details     │
              │ (conditions, medications, allergies)│
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │ Step 3: Collect Preferences & Style │
              │ (food likes, dislikes, budget, etc.)│
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │   User clicks "Generate Nutrition Plan" │
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │    LangGraph Workflow Starts        │
              └──────────────────┬──────────────────┘
                                 │
     ┌───────────────────────────┴────────────────────────────┐
     │                                                        │
```

┌──────────────┐                                       ┌──────────────────┐
│ AI Nutritionist│                                       │ Medical Specialist│
│ Agent generates│                                       │ Agent validates  │
│ meal plans     │                                       │ for safety       │
└──────────────┘                                       └──────────────────┘
│                                                        │
└───────────────────────────┬───────────────────────────┘
│
┌──────────▼──────────┐
│  Diet Planner Agent │
│ builds final plan   │
└──────────┬──────────┘
│
┌──────────▼──────────┐
│  Display Results to │
│      the User       │
└──────────┬──────────┘
│
┌──────────▼──────────┐
│ Show Meal Plan, Macros │
│  Hydration, Analytics  │
└──────────┬──────────┘
│
┌──────────▼──────────┐
│ Offer Export Options │
│ (Markdown download,  │
│ Email reminders)      │
└──────────┬──────────┘
│
┌──────────▼──────────┐
│ User can Chat with  │
│ AI Nutrition Coach  │
└──────────┬──────────┘
│
┌──────────▼──────────┐
│   End of Workflow   │
└─────────────────────┘

```

---

## 🧠 How It Works (LangGraph Overview)

The app is built as a **LangGraph workflow** where each step is a node in the graph.  
The output of one step becomes the input for the next step.

### 🗺️ Nodes:
- `Input Collection` → User input
- `AI Nutritionist Agent` → Meal plans
- `Medical Specialist Agent` → Validation
- `Diet Planner Agent` → Final plan creation
- `UI Display Node` → Results shown
- `Export Node` → User downloads plan or sets reminders
- `AI Chat Agent` → On-demand Q&A

### 🔄 Transitions:
- Sequential flow + conditional checks
- Agents operate asynchronously under CrewAI + LangGraph orchestration

### 💡 Benefits:
- Modularity: Each step can be extended/replaced
- Robust: Errors in any node can reroute or retry
- Reusable for any personalized health/nutrition application

---

## 📝 Summary of LangGraph Usage

SehaatSaathi.AI uses **LangGraph to build a decision tree graph**:
- Agents as nodes
- User actions and results as edges
- Modular, scalable, and easy to maintain

This architecture allows the app to function as a **true multi-agent AI system**.

---
```

---

This is ready to be **directly copy-pasted into your GitHub `README.md`** under the section:
👉 `## 🌳 LangGraph Decision Tree Workflow`



---

## 👨‍💻 Developed by: [TECHSEVA SOLUTIONS](https://github.com/abhishekkumar62000)

> If you like this project, don't forget to ⭐ star the repo and fork it for your own experiments!

---
