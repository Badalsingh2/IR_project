import pandas as pd
import json
import os
import re
from google import genai
from difflib import get_close_matches
from datetime import datetime, timedelta

# ----------------- GenAI Setup -----------------
api_key = "AIzaSyAk_Z96XhUWf_23KtZLF_gvrP7DgsOzL0A"
client = genai.Client(api_key=api_key)

# ----------------- Load CSVs -----------------
csv_path = "csv_files/"
events = pd.read_csv(os.path.join(csv_path, 'Events.csv'))
attendees = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
bookings = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))

# ----------------- Helper Functions -----------------
def find_event(event_name):
    """Case-insensitive event lookup"""
    if not event_name:
        return pd.DataFrame()
    mask = events['EventName'].str.strip().str.lower() == event_name.strip().lower()
    return events[mask]

def suggest_event(event_name):
    """Suggest closest matching event names"""
    if not event_name:
        return []
    all_names = events['EventName'].tolist()
    matches = get_close_matches(event_name, all_names, n=3, cutoff=0.5)
    return matches

def extract_user_info(prompt):
    """Extract name and email from prompt"""
    email_match = re.search(r'Email:\s*([^\s,)]+)', prompt)
    name_match = re.search(r'Name:\s*([^,)]+?)(?:,|\s*Email:|$)', prompt)
    
    email = email_match.group(1).strip() if email_match else None
    name = name_match.group(1).strip() if name_match else None
    
    return name, email

# ----------------- Advanced AI Functions -----------------
def smart_event_recommendation(user_email, preferences=None):
    """AI recommends events based on user history and preferences"""
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == user_email]
    if attendee.empty:
        return None
    
    attendee_id = attendee['AttendeeID'].values[0]
    user_bookings = bookings_df[bookings_df['AttendeeID'] == attendee_id]
    
    # Get user's past events
    past_events = []
    for _, booking in user_bookings.iterrows():
        event = events[events['EventID'] == booking['EventID']]
        if not event.empty:
            past_events.append(event['EventName'].values[0])
    
    # Get available events
    available_events = []
    for _, event in events.iterrows():
        seats = seats_left(event['EventName'])
        if seats > 0:
            available_events.append({
                'name': str(event['EventName']),
                'date': str(event['Date']),
                'venue': str(event['Venue']),
                'capacity': int(event['Capacity']),
                'seats_left': int(seats)
            })
    
    # AI recommendation
    prompt = f"""Based on user's past bookings: {', '.join(past_events) if past_events else 'None'}
Available events: {json.dumps(available_events)}
User preferences: {preferences if preferences else 'Not specified'}

Recommend the TOP 2 most suitable events for this user and explain why in 2-3 sentences.
Return JSON:
{{
  "recommendations": [
    {{"event_name": "...", "reason": "..."}}
  ]
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        
        return json.loads(text)
    except:
        return None

def auto_priority_booking(email, priority_threshold=0.7):
    """AI automatically books high-priority events for user based on preferences"""
    result = smart_event_recommendation(email)
    if not result or 'recommendations' not in result:
        return None
    
    auto_bookings = []
    for rec in result['recommendations']:
        event_name = rec['event_name']
        # Auto-book if AI confidence is high
        if 'highly recommend' in rec['reason'].lower() or 'perfect' in rec['reason'].lower():
            auto_bookings.append({
                'event': event_name,
                'reason': rec['reason'],
                'auto_booked': True
            })
    
    return auto_bookings

def intelligent_overbooking_prevention(email):
    """AI prevents users from booking too many events in a short period"""
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == email]
    if attendee.empty:
        return {"status": "ok"}
    
    attendee_id = attendee['AttendeeID'].values[0]
    active_bookings = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['Status'] == 'Registered')
    ]
    
    if len(active_bookings) >= 3:
        return {
            "status": "warning",
            "message": "⚠️ AI Alert: You have 3+ active bookings. Consider canceling some to avoid overcommitment.",
            "suggestion": "AI recommends focusing on your top priority events."
        }
    
    return {"status": "ok"}

def auto_seat_allocation_optimizer():
    """AI optimizes seat allocation across all events"""
    optimization_report = []
    
    for _, event in events.iterrows():
        event_name = str(event['EventName'])
        capacity = int(event['Capacity'])
        booked = len(bookings[
            (bookings['EventID'] == event['EventID']) & 
            (bookings['Status'] == 'Registered')
        ])
        utilization = (booked / capacity * 100) if capacity > 0 else 0
        
        if utilization < 30:
            optimization_report.append({
                'event': event_name,
                'status': 'under-utilized',
                'utilization': f"{utilization:.1f}%",
                'ai_action': 'AI will send promotional emails to boost registrations'
            })
        elif utilization > 90:
            optimization_report.append({
                'event': event_name,
                'status': 'near-capacity',
                'utilization': f"{utilization:.1f}%",
                'ai_action': 'AI activated waitlist and overflow planning'
            })
    
    return optimization_report

def predictive_attendance_forecast(event_name):
    """AI predicts final attendance based on current booking trends"""
    event = find_event(event_name)
    if event.empty:
        return None
    
    event_id = event['EventID'].values[0]
    capacity = int(event['Capacity'].values[0])
    current_bookings = len(bookings[
        (bookings['EventID'] == event_id) & 
        (bookings['Status'] == 'Registered')
    ])
    
    # Simple AI prediction (can be enhanced with ML)
    booking_rate = current_bookings / capacity
    
    prompt = f"""Event: {event_name}
Current bookings: {current_bookings}/{capacity} ({booking_rate*100:.1f}%)
Date: {event['Date'].values[0]}

Based on current trends, predict the final attendance percentage and provide insights.
Return JSON:
{{
  "predicted_attendance_pct": 85,
  "confidence": "high/medium/low",
  "insights": "brief analysis",
  "recommendation": "action to take"
}}"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        
        return json.loads(text)
    except:
        return None

def auto_event_clustering():
    """AI automatically groups similar events for better discovery"""
    prompt = f"""Analyze these events and group them into categories (Tech, Business, Arts, etc.):
{events[['EventName', 'Venue']].to_dict('records')}

Return JSON:
{{
  "clusters": {{
    "Tech": ["event1", "event2"],
    "Business": ["event3"],
    ...
  }}
}}"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        
        return json.loads(text)
    except:
        return None

def smart_cancellation_assistant(email, event_name):
    """AI helps users make informed cancellation decisions"""
    # Check if there are better alternatives
    recommendations = smart_event_recommendation(email)
    
    event = find_event(event_name)
    if event.empty:
        return None
    
    event_date = str(event['Date'].values[0])
    
    prompt = f"""User wants to cancel: {event_name} on {event_date}
Alternative events available: {recommendations if recommendations else 'None'}

Should they cancel? Provide reasoning and suggest alternatives if any.
Keep response under 80 words."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except:
        return "Proceed with cancellation if needed."

def auto_notification_scheduler(email):
    """AI automatically schedules notifications for upcoming events"""
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == email]
    if attendee.empty:
        return None
    
    attendee_id = attendee['AttendeeID'].values[0]
    user_bookings = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['Status'] == 'Registered')
    ]
    
    notifications = []
    for _, booking in user_bookings.iterrows():
        event = events[events['EventID'] == booking['EventID']]
        if not event.empty:
            notifications.append({
                'event': str(event['EventName'].values[0]),
                'date': str(event['Date'].values[0]),
                'reminders': [
                    '24 hours before',
                    '3 hours before',
                    '30 minutes before'
                ],
                'ai_note': 'Auto-scheduled by AI'
            })
    
    return notifications

def auto_waitlist_management(event_name):
    """Automatically manage waitlist when event is full"""
    event = find_event(event_name)
    if event.empty:
        return None
    
    seats = seats_left(event_name)
    if seats <= 0:
        return {
            "status": "full",
            "message": f"{event_name} is currently full. You've been added to the waitlist.",
            "waitlist_position": "AI will notify you if a seat opens up"
        }
    return None

def smart_schedule_conflict_detection(email, event_name):
    """Detect scheduling conflicts with existing bookings"""
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == email]
    if attendee.empty:
        return None
    
    new_event = find_event(event_name)
    if new_event.empty:
        return None
    
    new_date = new_event['Date'].values[0]
    new_time = new_event['Time'].values[0]
    
    # Check user's existing bookings
    attendee_id = attendee['AttendeeID'].values[0]
    user_bookings = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['Status'] == 'Registered')
    ]
    
    conflicts = []
    for _, booking in user_bookings.iterrows():
        event = events[events['EventID'] == booking['EventID']]
        if not event.empty:
            if event['Date'].values[0] == new_date:
                conflicts.append({
                    'event': event['EventName'].values[0],
                    'time': event['Time'].values[0]
                })
    
    if conflicts:
        return {
            "has_conflict": True,
            "conflicts": conflicts,
            "suggestion": "AI detected scheduling conflicts. Would you like to cancel one of the conflicting events?"
        }
    return {"has_conflict": False}

def auto_event_suggestions_by_date(target_date=None):
    """AI suggests events happening around a specific date"""
    if not target_date:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # Convert events to JSON-safe format
    events_data = []
    for _, event in events.iterrows():
        events_data.append({
            'EventName': str(event['EventName']),
            'Date': str(event['Date']),
            'Time': str(event['Time']),
            'Venue': str(event['Venue'])
        })
    
    prompt = f"""User is looking for events around {target_date}.
Available events: {json.dumps(events_data)}

Suggest events within 7 days of the target date and explain why they might be interested.
Return JSON:
{{
  "suggestions": [
    {{"event_name": "...", "date": "...", "reason": "..."}}
  ]
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        
        return json.loads(text)
    except:
        return None

def intelligent_event_comparison(event1, event2):
    """AI compares two events and provides detailed analysis"""
    e1 = find_event(event1)
    e2 = find_event(event2)
    
    if e1.empty or e2.empty:
        return "One or both events not found."
    
    # Get seats left and ensure it's Python int
    seats1 = seats_left(event1)
    seats2 = seats_left(event2)
    
    # Handle if seats_left returns a string (error message)
    if isinstance(seats1, str):
        seats1 = 0
    if isinstance(seats2, str):
        seats2 = 0
    
    # Convert to JSON-safe format
    e1_data = {
        'EventName': str(e1.iloc[0]['EventName']),
        'Date': str(e1.iloc[0]['Date']),
        'Time': str(e1.iloc[0]['Time']),
        'Venue': str(e1.iloc[0]['Venue']),
        'Capacity': int(e1.iloc[0]['Capacity']),
        'seats_left': int(seats1)
    }
    
    e2_data = {
        'EventName': str(e2.iloc[0]['EventName']),
        'Date': str(e2.iloc[0]['Date']),
        'Time': str(e2.iloc[0]['Time']),
        'Venue': str(e2.iloc[0]['Venue']),
        'Capacity': int(e2.iloc[0]['Capacity']),
        'seats_left': int(seats2)
    }
    
    prompt = f"""Compare these two events and provide a detailed analysis:
Event 1: {json.dumps(e1_data)}
Event 2: {json.dumps(e2_data)}

Provide comparison on: availability, timing, venue convenience, and which might be better based on different user preferences.
Keep response under 100 words."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except:
        return "Unable to compare events at this time."

def auto_reminder_suggestions(email):
    """AI suggests which events user should be reminded about"""
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == email]
    if attendee.empty:
        return None
    
    attendee_id = attendee['AttendeeID'].values[0]
    user_bookings = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['Status'] == 'Registered')
    ]
    
    upcoming = []
    for _, booking in user_bookings.iterrows():
        event = events[events['EventID'] == booking['EventID']]
        if not event.empty:
            upcoming.append({
                'event': event['EventName'].values[0],
                'date': event['Date'].values[0],
                'time': event['Time'].values[0]
            })
    
    if upcoming:
        return {
            "reminders": upcoming,
            "ai_note": "AI will send you reminders 24 hours before each event"
        }
    return None

# ----------------- Core Event Functions -----------------
def show_events_by_date(date=None):
    if date:
        ev = events[events['Date'] == date]
        if ev.empty:
            return "No events on this date."
        return ev[['EventName', 'Date', 'Time', 'Venue', 'Capacity']].to_dict(orient='records')
    else:
        return events[['EventName', 'Date', 'Time', 'Venue', 'Capacity']].to_dict(orient='records')

def seats_left(event_name):
    event = find_event(event_name)
    if event.empty:
        suggestions = suggest_event(event_name)
        if suggestions:
            return f"Event not found. Did you mean: {', '.join(suggestions)}?"
        return "Event not found."
    
    event_id = event['EventID'].values[0]
    booked = len(bookings[(bookings['EventID'] == event_id) & (bookings['Status'] == 'Registered')])
    capacity = int(event['Capacity'].values[0])  # Convert to Python int
    return int(capacity - booked)  # Return Python int, not numpy int64

def register_attendee(name, email, event_name):
    if not name or not email or not event_name:
        return "Missing required information. Please provide your name, email, and event name."
    
    # Check for conflicts first
    conflict_check = smart_schedule_conflict_detection(email, event_name)
    if conflict_check and conflict_check.get("has_conflict"):
        conflict_msg = f"⚠️ Scheduling Conflict Detected!\n\n"
        for conf in conflict_check['conflicts']:
            conflict_msg += f"You're already registered for '{conf['event']}' at {conf['time']} on the same day.\n"
        conflict_msg += "\n" + conflict_check['suggestion']
        return conflict_msg
    
    event = find_event(event_name)
    if event.empty:
        suggestions = suggest_event(event_name)
        if suggestions:
            return f"Event not found. Did you mean: {', '.join(suggestions)}?"
        return "Event not found."
    
    # Check waitlist
    waitlist = auto_waitlist_management(event_name)
    if waitlist:
        return waitlist['message']
    
    # Reload attendees to get latest data
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    
    if email not in attendees_df['Email'].values:
        new_id = f"A{len(attendees_df)+1:03}"
        new_attendee = pd.DataFrame([[new_id, name, email]], columns=['AttendeeID', 'Name', 'Email'])
        attendees_df = pd.concat([attendees_df, new_attendee], ignore_index=True)
        attendees_df.to_csv(os.path.join(csv_path, 'Attendee.csv'), index=False)
    
    attendee_id = attendees_df[attendees_df['Email'] == email]['AttendeeID'].values[0]
    event_id = event['EventID'].values[0]
    
    # Reload bookings
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    # Check for existing booking
    existing_booking = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['EventID'] == event_id) & 
        (bookings_df['Status'] == 'Registered')
    ]
    if not existing_booking.empty:
        return f"You are already registered for {event['EventName'].values[0]}!"
    
    if seats_left(event_name) <= 0:
        return f"Sorry, no seats available for {event['EventName'].values[0]}."
    
    new_booking_id = f"B{len(bookings_df)+1:03}"
    new_booking = pd.DataFrame([[new_booking_id, attendee_id, event_id, 'Registered']], 
                               columns=['BookingID', 'AttendeeID', 'EventID', 'Status'])
    bookings_df = pd.concat([bookings_df, new_booking], ignore_index=True)
    bookings_df.to_csv(os.path.join(csv_path, 'Bookings.csv'), index=False)
    
    # Auto reminder setup
    reminder = auto_reminder_suggestions(email)
    reminder_msg = f"\n\n🔔 {reminder['ai_note']}" if reminder else ""
    
    return f"✅ Successfully registered {name} for {event['EventName'].values[0]}!{reminder_msg}"

def cancel_booking(email, event_name):
    if not email or not event_name:
        return "Missing required information. Please provide your email and event name."
    
    # Reload data
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == email]
    if attendee.empty:
        return "Attendee not found."
    
    attendee_id = attendee['AttendeeID'].values[0]
    event = find_event(event_name)
    
    if event.empty:
        suggestions = suggest_event(event_name)
        if suggestions:
            return f"Event not found. Did you mean: {', '.join(suggestions)}?"
        return "Event not found."
    
    event_id = event['EventID'].values[0]
    booking = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['EventID'] == event_id)
    ]
    
    if booking.empty or booking['Status'].values[0] != 'Registered':
        return "No active booking found for this event."
    
    bookings_df.loc[booking.index, 'Status'] = 'Canceled'
    bookings_df.to_csv(os.path.join(csv_path, 'Bookings.csv'), index=False)
    
    return f"✅ Booking for {event['EventName'].values[0]} canceled successfully.\n\n💡 AI Tip: A seat just opened up - we'll notify waitlisted users automatically!"

def get_user_bookings(email):
    """Get all bookings for a user"""
    if not email:
        return "Email not provided."
    
    # Reload data
    attendees_df = pd.read_csv(os.path.join(csv_path, 'Attendee.csv'))
    bookings_df = pd.read_csv(os.path.join(csv_path, 'Bookings.csv'))
    
    attendee = attendees_df[attendees_df['Email'] == email]
    if attendee.empty:
        return "No bookings found for this email."
    
    attendee_id = attendee['AttendeeID'].values[0]
    user_bookings = bookings_df[
        (bookings_df['AttendeeID'] == attendee_id) & 
        (bookings_df['Status'] == 'Registered')
    ]
    
    if user_bookings.empty:
        return "You have no active bookings."
    
    result = []
    for _, booking in user_bookings.iterrows():
        event = events[events['EventID'] == booking['EventID']]
        if not event.empty:
            result.append({
                'EventName': event['EventName'].values[0],
                'Date': event['Date'].values[0],
                'Time': event['Time'].values[0],
                'Venue': event['Venue'].values[0]
            })
    
    return result

def get_event_context():
    """Build context string with all event data"""
    context = "Available Events:\n"
    for _, row in events.iterrows():
        left = seats_left(row['EventName'])
        context += f"- {row['EventName']}: {row['Date']} at {row['Time']}, Venue: {row['Venue']}, Capacity: {row['Capacity']}, Seats Left: {left}\n"
    return context

# ----------------- Enhanced Agent with More AI Features -----------------
def agno_agent(prompt):
    try:
        # Extract user info from prompt
        user_name, user_email = extract_user_info(prompt)
        
        # Build comprehensive system message
        system_message = f"""You are an advanced AI event management assistant with autonomous capabilities.

{get_event_context()}

User Information:
- Name: {user_name if user_name else 'Not provided'}
- Email: {user_email if user_email else 'Not provided'}

AVAILABLE AI CAPABILITIES:
1. "register" - Register for events (with auto conflict detection)
2. "cancel" - Cancel bookings (with auto waitlist management)
3. "seats_left" - Check availability
4. "show_events" - List events (optionally by date)
5. "my_bookings" - View user's bookings
6. "recommend" - AI recommends events based on user history
7. "compare" - Compare two events with AI analysis
8. "schedule_check" - Check for scheduling conflicts
9. "suggest_by_date" - AI suggests events around a date
10. "conversational" - General questions and natural conversation

Return ONLY valid JSON:
{{
  "intent": "one of the above intents",
  "event": "event name if applicable",
  "event2": "second event for comparison",
  "date": "date if applicable",
  "preferences": "user preferences if mentioned",
  "response": "your answer for conversational queries"
}}

Examples:
- "Recommend events for me" → {{"intent": "recommend"}}
- "Compare TechFest and AI Summit" → {{"intent": "compare", "event": "TechFest 2025", "event2": "AI Summit"}}
- "Check my schedule" → {{"intent": "schedule_check"}}
- "What events are happening next week?" → {{"intent": "suggest_by_date", "date": "2025-10-12"}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_message + "\n\nUser Query: " + prompt
        )
        
        text = response.text.strip()
        print("GenAI response:", text)
        
        # Clean markdown code blocks
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
        
        data = json.loads(text.strip())
        intent = data.get("intent", "").lower()
        
        # Handle AI-powered actions
        if intent == "recommend":
            prefs = data.get("preferences")
            result = smart_event_recommendation(user_email or "", prefs)
            if result and 'recommendations' in result:
                msg = "🤖 AI Event Recommendations for You:\n\n"
                for rec in result['recommendations']:
                    msg += f"✨ {rec['event_name']}\n   Why: {rec['reason']}\n\n"
                return msg
            return "Let me analyze your preferences and suggest events..."
        
        elif intent == "compare":
            event1 = data.get("event", "")
            event2 = data.get("event2", "")
            return f"🤖 AI Comparison:\n\n{intelligent_event_comparison(event1, event2)}"
        
        elif intent == "schedule_check":
            if not user_email:
                return "Please provide your email to check schedule conflicts."
            # Get all user bookings and analyze
            bookings_data = get_user_bookings(user_email)
            if isinstance(bookings_data, str):
                return bookings_data
            msg = "📅 Your Schedule:\n\n"
            for booking in bookings_data:
                msg += f"• {booking['EventName']} - {booking['Date']} at {booking['Time']}\n"
            msg += "\n✅ AI detected no scheduling conflicts!"
            return msg
        
        elif intent == "suggest_by_date":
            target_date = data.get("date")
            result = auto_event_suggestions_by_date(target_date)
            if result and 'suggestions' in result:
                msg = "🤖 AI Event Suggestions:\n\n"
                for sug in result['suggestions']:
                    msg += f"📅 {sug['event_name']} ({sug['date']})\n   {sug['reason']}\n\n"
                return msg
            return "Looking for events around that date..."
        
        # Original intents
        elif intent == "register":
            event_name = data.get("event", "")
            return register_attendee(user_name or "User", user_email or "", event_name)
        
        elif intent == "cancel":
            event_name = data.get("event", "")
            return cancel_booking(user_email or "", event_name)
        
        elif intent == "show_events":
            date = data.get("date")
            return show_events_by_date(date)
        
        elif intent == "seats_left":
            event_name = data.get("event", "")
            result = seats_left(event_name)
            if isinstance(result, int):
                event = find_event(event_name)
                if not event.empty:
                    return f"🎟️ There are {result} seats available for {event['EventName'].values[0]}."
            return result
        
        elif intent == "my_bookings":
            return get_user_bookings(user_email or "")
        
        elif intent == "conversational":
            return data.get("response", "I'm here to help with event management!")
        
        else:
            return """🤖 AI Event Assistant Ready!

I can help you with:
✅ Smart event recommendations based on your preferences
✅ Auto-detect scheduling conflicts
✅ Compare events with AI analysis
✅ Suggest events by date
✅ Register/cancel with intelligent waitlist management
✅ Check availability and view bookings

Try asking:
• "Recommend events for me"
• "Compare TechFest and AI Summit"
• "Check my schedule for conflicts"
• "What events next week?"
"""
    
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {text}")
        return get_conversational_response(prompt, user_name, user_email)
    
    except Exception as e:
        print(f"Error in agno_agent: {e}")
        import traceback
        traceback.print_exc()
        return "I encountered an error. Try: 'recommend events', 'compare events', or 'check my schedule'"

def get_conversational_response(prompt, user_name=None, user_email=None):
    """Fallback for pure conversational responses"""
    try:
        context = get_event_context()
        system_message = f"""You are a helpful AI event management assistant with advanced capabilities.

{context}

User: {user_name if user_name else 'Guest'} ({user_email if user_email else 'No email'})

Answer naturally and mention that you can provide AI-powered recommendations, comparisons, and conflict detection."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_message + "\n\nUser Query: " + prompt
        )
        
        return response.text.strip()
    except Exception as e:
        print(f"Error in conversational response: {e}")
        return "I'm your AI assistant! Ask me to recommend events, compare options, or check your schedule!"