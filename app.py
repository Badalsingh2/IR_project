import streamlit as st
import pandas as pd
import os
from event_agent import agno_agent
from datetime import datetime

# ----------------- Paths & CSVs -----------------
csv_path = "csv_files/"
events_file = os.path.join(csv_path, 'Events.csv')
attendees_file = os.path.join(csv_path, 'Attendee.csv')
bookings_file = os.path.join(csv_path, 'Bookings.csv')

events = pd.read_csv(events_file)
attendees = pd.read_csv(attendees_file)
bookings = pd.read_csv(bookings_file)

# ----------------- Streamlit Config -----------------
st.set_page_config(
    page_title="AI Event Management",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Custom CSS -----------------
st.markdown("""
<style>
/* ---------- General App Styling ---------- */
.main {
    background-color: #f0f2f6; /* softer gray background */
    color: #222; /* default text color for better readability */
    font-family: 'Segoe UI', sans-serif;
}

/* ---------- AI Badge ---------- */
.ai-badge {
    background: linear-gradient(135deg, #5a67d8 0%, #805ad5 100%);
    color: #fff;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    margin-right: 0.5rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* ---------- Feature Cards ---------- */
.feature-card {
    background: #ffffff;
    padding: 1.2rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    margin-bottom: 1.2rem;
    border-left: 5px solid #667eea;
    color: #333; /* darker text */
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
}

/* ---------- App Header ---------- */
.app-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.2rem;
    border-radius: 12px;
    color: #fff;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}

.app-header h1, .app-header h2, .app-header p {
    color: #fff;
}

/* ---------- AI Suggestion Box ---------- */
.ai-suggestion {
    background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
    padding: 1rem;
    border-radius: 10px;
    color: #fff;
    margin: 1.2rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* ---------- Quick Action Buttons ---------- */
.quick-action-btn {
    background: #fff;
    border: 2px solid #667eea;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    cursor: pointer;
    color: #333;
    font-weight: 500;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.quick-action-btn:hover {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border-color: transparent;
    transform: scale(1.02);
}

/* ---------- Stats Cards ---------- */
.stat-card {
    background: #fff;
    padding: 1.2rem;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    text-align: center;
    color: #333;
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #5a67d8;
}

/* ---------- AI Chat Container ---------- */
.ai-chat-container {
    background: #f8f9ff;
    padding: 1.5rem;
    border-radius: 12px;
    border: 2px solid #667eea;
    margin-top: 1rem;
    color: #222;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)


# ----------------- Helper Functions -----------------
def get_user_stats(email):
    attendee = attendees[attendees['Email'] == email]
    if attendee.empty:
        return 0, 0
    
    attendee_id = attendee['AttendeeID'].values[0]
    user_bookings = bookings[bookings['AttendeeID'] == attendee_id]
    active = len(user_bookings[user_bookings['Status'] == 'Registered'])
    total = len(user_bookings)
    
    return active, total

# ----------------- Session State -----------------
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_ai_features' not in st.session_state:
    st.session_state.show_ai_features = True

# ----------------- Sidebar -----------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("🤖 AI Assistant")
    st.markdown("---")
    
    if st.session_state.email != "":
        st.markdown(f"### 👤 {st.session_state.name}")
        st.markdown(f"📧 {st.session_state.email}")
        
        active, total = get_user_stats(st.session_state.email)
        
        st.markdown("---")
        st.markdown("### 📊 Your Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active", active)
        with col2:
            st.metric("Total", total)
        
        st.markdown("---")
        st.markdown("### 🤖 AI Powers")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; font-size: 0.85rem;">
        <b>✨ What AI Does:</b><br>
        • Auto-detects conflicts<br>
        • Smart recommendations<br>
        • Intelligent comparisons<br>
        • Waitlist management<br>
        • Schedule optimization<br>
        • Auto reminders
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.email = ""
            st.session_state.name = ""
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("Login to unlock AI-powered features!")
        st.markdown("### 🤖 AI Features")
        st.markdown("""
        - Smart Event Recommendations
        - Auto Conflict Detection
        - Intelligent Event Comparison
        - Waitlist Management
        - Schedule Optimization
        """)

# ----------------- Main Content -----------------

# Header
st.markdown("""
    <div class="app-header">
        <h1>🤖 AI-Powered Event Management</h1>
        <p>Experience Intelligent Automation for Seamless Event Planning</p>
        <span class="ai-badge">🧠 AI ENABLED</span>
        <span class="ai-badge">⚡ AUTO-OPTIMIZATION</span>
        <span class="ai-badge">🎯 SMART RECOMMENDATIONS</span>
    </div>
""", unsafe_allow_html=True)

# ----------------- Login / Registration -----------------
if st.session_state.email == "":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔐 Login")
        with st.form("login_form"):
            email_login = st.text_input("Email Address", key="login_email")
            submit_login = st.form_submit_button("Login", use_container_width=True)
            
            if submit_login:
                user = attendees[attendees['Email'].str.lower() == email_login.strip().lower()]
                if user.empty:
                    st.error("❌ Email not found. Please register first.")
                else:
                    st.session_state.email = email_login.strip()
                    st.session_state.name = user['Name'].values[0]
                    st.success(f"✅ Welcome back, {st.session_state.name}!")
                    st.rerun()
    
    with col2:
        st.markdown("### 📝 Register")
        with st.form("register_form"):
            name_register = st.text_input("Full Name", key="register_name")
            email_register = st.text_input("Email Address", key="register_email")
            submit_register = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_register:
                if email_register.strip() == "" or name_register.strip() == "":
                    st.error("❌ Please fill in all fields.")
                elif email_register.strip().lower() in attendees['Email'].str.lower().values:
                    st.error("❌ Email already registered. Please login.")
                else:
                    new_id = f"A{len(attendees)+1:03}"
                    new_attendee = pd.DataFrame([[new_id, name_register.strip(), email_register.strip()]], 
                                               columns=['AttendeeID', 'Name', 'Email'])
                    attendees = pd.concat([attendees, new_attendee], ignore_index=True)
                    attendees.to_csv(attendees_file, index=False)
                    st.session_state.email = email_register.strip()
                    st.session_state.name = name_register.strip()
                    st.success(f"✅ Account created! Welcome, {st.session_state.name}!")
                    st.rerun()

# ----------------- Dashboard (Logged In) -----------------
else:
    # Welcome with AI Features
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
            <h2>👋 Welcome back, {st.session_state.name}!</h2>
            <p>🤖 AI is actively monitoring your events and optimizing your schedule</p>
        </div>
    """, unsafe_allow_html=True)
    
    # AI-Powered Quick Actions
    st.markdown("### ⚡ AI Automation Dashboard")
    
    # Create tabs for different automation features
    tab1, tab2, tab3 = st.tabs(["🎯 Smart Actions", "📊 AI Analytics", "🔔 Automation"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Get AI Recommendations", use_container_width=True):
                prompt = f"Recommend events for me (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("🤖 AI analyzing your preferences..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Get recommendations", "bot": response})
                    st.info(response)
        
            if st.button("⚡ AI Auto-Book Priority Events", use_container_width=True):
                prompt = f"Auto book priority events for me (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("🤖 AI finding perfect matches..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Auto-book", "bot": response})
                    st.warning(response)
        
        with col2:
            if st.button("📅 Check Overbooking Risk", use_container_width=True):
                prompt = f"Check if I'm overbooking (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("🤖 AI checking your schedule..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Overbook check", "bot": response})
                    st.success(response)
            
            if st.button("📋 My Bookings + AI Insights", use_container_width=True):
                prompt = f"Show my bookings (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("Loading your bookings..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Show bookings", "bot": response})
                    if isinstance(response, list):
                        for booking in response:
                            st.write(f"✅ {booking['EventName']} - {booking['Date']}")
                    else:
                        st.write(response)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 AI Seat Optimization Report", use_container_width=True):
                prompt = "Show seat optimization report"
                with st.spinner("🤖 AI optimizing seat allocation..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Optimization report", "bot": response})
                    st.info(response)
            
            if st.button("📁 AI Event Clustering", use_container_width=True):
                prompt = "Cluster events by category"
                with st.spinner("🤖 AI categorizing events..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Cluster events", "bot": response})
                    st.success(response)
        
        with col2:
            event_for_prediction = st.selectbox("Select event for AI prediction:", 
                                               events['EventName'].tolist())
            if st.button("🔮 Predict Attendance", use_container_width=True):
                prompt = f"Predict attendance for {event_for_prediction}"
                with st.spinner("🤖 AI analyzing trends..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": f"Predict {event_for_prediction}", "bot": response})
                    st.info(response)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔔 View Auto-Scheduled Notifications", use_container_width=True):
                prompt = f"Show notification schedule (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("🤖 Loading AI notifications..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Notification schedule", "bot": response})
                    st.success(response)
            
            if st.button("📅 AI Schedule Conflict Check", use_container_width=True):
                prompt = f"Check my schedule for conflicts (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("🤖 AI checking for conflicts..."):
                    response = agno_agent(prompt)
                    st.session_state.chat_history.append({"user": "Check schedule", "bot": response})
                    st.success(response)
        
        with col2:
            if st.button("🔍 Compare Top 2 Events", use_container_width=True):
                if len(events) >= 2:
                    event1 = events.iloc[0]['EventName']
                    event2 = events.iloc[1]['EventName']
                    prompt = f"Compare {event1} and {event2}"
                    with st.spinner("🤖 AI comparing events..."):
                        response = agno_agent(prompt)
                        st.session_state.chat_history.append({"user": f"Compare events", "bot": response})
                        st.info(response)
                else:
                    st.warning("Not enough events to compare")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # AI Features Showcase
    st.markdown("### 🤖 AI Automation in Action")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h4>🎯 Smart Recommendations</h4>
                <p style="font-size: 0.9rem; color: #666;">AI analyzes your booking history and preferences to suggest perfect events for you</p>
                <span class="ai-badge">AUTO</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <h4>⚠️ Conflict Detection</h4>
                <p style="font-size: 0.9rem; color: #666;">Automatically detects scheduling conflicts before you book and suggests alternatives</p>
                <span class="ai-badge">REAL-TIME</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <h4>📊 Intelligent Comparison</h4>
                <p style="font-size: 0.9rem; color: #666;">AI compares events on multiple factors to help you make the best choice</p>
                <span class="ai-badge">AI-POWERED</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Events Display with AI Insights
    st.markdown("### 🎉 Available Events")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Search events (AI-enhanced)", placeholder="Try: 'tech events' or 'evening events'")
    with col2:
        sort_by = st.selectbox("Sort by", ["AI Recommended", "Date", "Name", "Availability"])
    
    # Filter events
    filtered_events = events.copy()
    if search_term:
        filtered_events = filtered_events[
            filtered_events['EventName'].str.contains(search_term, case=False) |
            filtered_events['Venue'].str.contains(search_term, case=False)
        ]
    
    # Display events
    for idx, row in filtered_events.iterrows():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Calculate AI score (simple popularity)
            booked = len(bookings[(bookings['EventID'] == row['EventID']) & (bookings['Status'] == 'Registered')])
            popularity = int((booked / row['Capacity']) * 100) if row['Capacity'] > 0 else 0
            
            ai_insight = ""
            if popularity > 70:
                ai_insight = "<span class='ai-badge'>🔥 TRENDING</span>"
            elif popularity < 30:
                ai_insight = "<span class='ai-badge'>✨ AVAILABLE</span>"
            
            st.markdown(f"""
                <div class="feature-card">
                    <h3 style="margin-top:0; color: #667eea;">🎪 {row['EventName']} {ai_insight}</h3>
                    <p><strong>📅</strong> {row['Date']} | <strong>⏰</strong> {row['Time']} | <strong>📍</strong> {row['Venue']}</p>
                    <p><strong>💺 Seats:</strong> {row['Capacity']} | <strong>📊 Popularity:</strong> {popularity}%</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"🤖 AI Register", key=f"reg_{row['EventID']}", use_container_width=True):
                prompt = f"Register me for {row['EventName']} (Name: {st.session_state.name}, Email: {st.session_state.email})"
                with st.spinner("🤖 AI checking conflicts & availability..."):
                    response = agno_agent(prompt)
                    st.toast(response, icon="🤖")
                    st.session_state.chat_history.append({"user": f"Register for {row['EventName']}", "bot": response})
                    if "✅" in response:
                        st.balloons()
                    st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # AI Chat Interface
    st.markdown("### 💬 AI Event Assistant")
    st.markdown("""
        <div class="ai-chat-container">
            <h4 style="margin-top:0;">🤖 Ask Me Anything!</h4>
            <p style="color: #666; font-size: 0.9rem;">I can recommend events, compare options, check conflicts, and more...</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Suggested prompts
    st.markdown("**💡 Try these AI-powered queries:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Recommend events for me", key="suggest1"):
            st.session_state.quick_prompt = "Recommend events for me"
    
    with col2:
        if st.button("🔍 Compare TechFest vs AI Summit", key="suggest2"):
            st.session_state.quick_prompt = "Compare TechFest 2025 and AI Summit"
    
    with col3:
        if st.button("📅 Events next week", key="suggest3"):
            st.session_state.quick_prompt = "What events are happening next week?"
    
    # Chat input
    if 'quick_prompt' in st.session_state:
        user_prompt = st.text_input("Your question to AI:", value=st.session_state.quick_prompt, key="chat_input")
        del st.session_state.quick_prompt
    else:
        user_prompt = st.text_input("Your question to AI:", placeholder="Ask anything about events...", key="chat_input")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("🤖 Ask AI", use_container_width=True)
    
    if send_button and user_prompt:
        full_prompt = f"{user_prompt} (Name: {st.session_state.name}, Email: {st.session_state.email})"
        
        with st.spinner("🤖 AI is thinking..."):
            response = agno_agent(full_prompt)
        
        st.session_state.chat_history.append({"user": user_prompt, "bot": response})
        
        # Display response
        if isinstance(response, list):
            st.markdown("#### 📋 AI Results:")
            for ev in response:
                st.markdown(f"""
                    <div class="feature-card">
                        <h4 style="margin-top:0;">{ev['EventName']}</h4>
                        <p><strong>📅</strong> {ev.get('Date', 'N/A')} | <strong>⏰</strong> {ev.get('Time', 'N/A')}</p>
                        <p><strong>📍</strong> {ev.get('Venue', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="ai-suggestion">
                    <strong>🤖 AI Response:</strong><br>
                    {response}
                </div>
            """, unsafe_allow_html=True)
    
    # Chat History
    if st.session_state.chat_history:
        st.markdown("#### 💬 Recent AI Conversations")
        for idx, chat in enumerate(reversed(st.session_state.chat_history[-3:])):
            with st.expander(f"💭 {chat['user']}", expanded=(idx==0)):
                st.markdown(f"**🤖 AI:** {chat['bot']}")

# Footer
st.markdown("<br>" * 2, unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem; background: white; border-radius: 10px;">
        <h4>🤖 Powered by Advanced AI Technology</h4>
        <p style="font-size: 0.9rem;">
            <span class="ai-badge">Auto Conflict Detection</span>
            <span class="ai-badge">Smart Recommendations</span>
            <span class="ai-badge">Intelligent Analysis</span>
            <span class="ai-badge">Real-time Optimization</span>
        </p>
        <p style="font-size: 0.85rem; margin-top: 1rem;">© 2025 AI Event Management System</p>
    </div>
""", unsafe_allow_html=True)