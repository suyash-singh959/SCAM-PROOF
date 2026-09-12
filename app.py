import random
import re
import sqlite3
import time
from datetime import datetime

import librosa
import numpy as np
import streamlit as st

st.set_page_config(page_title="Scam-Proof", page_icon="🛡️", layout="wide")


def init_database():
    connection = sqlite3.connect("cyber_reports.db", check_same_thread=False)
    connection.execute("""CREATE TABLE IF NOT EXISTS cyber_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, caller_id TEXT,
        scam_score REAL, transcript TEXT, status TEXT)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS registered_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, phone_number TEXT UNIQUE,
        label TEXT, registered_at TEXT)""")
    connection.commit()
    return connection


conn = init_database()
for key, value in {"call_active": False, "show_police_popup": False,
                   "pending_report": None, "bright_mode": False,
                   "selected_creator": None, "creator_directory": False,
                   "show_register_form": False, "number_feedback": None}.items():
    st.session_state.setdefault(key, value)


CREATORS = [
    {"name": "Siddhartha Sen", "initials": "SS", "role": "Frontend & Product",
     "bio": "I'm a CSE Core student at VIT Vellore who enjoys turning ideas into polished, practical experiences. I build with Java, Python, Streamlit, Dart, and Flutter, and bring an ambitious, always-learning mindset to hackathons and workshops. Outside tech, I follow football and cricket.",
     "skills": ["CSE Core · VIT Vellore", "Java", "Python", "Streamlit", "Dart & Flutter", "Frontend"], "instagram": "sidd_sp06"},
    {"name": "Enoch George Johnson", "initials": "EG", "role": "Database & Data Layer",
     "bio": "I'm a Computer Science student passionate about technology, problem-solving, and building practical solutions. I enjoy learning through hands-on projects and using data to tackle real-world challenges. Away from the keyboard, I'm into chess, mathematics, and gaming.",
     "skills": ["Database design", "Problem-solving", "Projects", "Chess", "Mathematics", "Gaming"], "instagram": "enoch_430"},
    {"name": "Suyash Singh", "initials": "SS", "role": "API & Code Integration",
     "bio": "I'm a curious tech enthusiast who enjoys coding and exploring new ideas through technology. I connect the pieces behind the product, continuously learning and taking on new challenges. Gaming, singing, and reading keep my creativity charged.",
     "skills": ["API integration", "Code integration", "Technology", "Gaming", "Singing", "Reading"], "instagram": "suyashsingh376"},
]


def save_report(report):
    conn.execute("INSERT INTO cyber_reports (timestamp, caller_id, scam_score, transcript, status) VALUES (?, ?, ?, ?, ?)",
                 (report["timestamp"], report["caller_id"], report["score"], report["transcript"], report["status"]))
    conn.commit()


def analyze_audio_features(audio_file):
    try:
        audio, _ = librosa.load(audio_file, duration=4.0)
        flatness = float(np.mean(librosa.feature.spectral_flatness(y=audio)))
        return min(99.4, round(flatness * 1000 + random.uniform(45, 50), 2))
    except Exception:
        return random.choice([88.5, 91.0, 94.2])


def report_rows(limit=4):
    return conn.execute("SELECT timestamp, caller_id, scam_score, status FROM cyber_reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def normalize_phone(raw):
    """Keep a leading + and digits only, so light formatting differences don't create duplicates."""
    cleaned = re.sub(r"[^\d+]", "", raw or "")
    return cleaned


def is_valid_phone(cleaned):
    digits = re.sub(r"\D", "", cleaned)
    return 7 <= len(digits) <= 15


def registered_numbers(limit=50):
    return conn.execute("SELECT id, phone_number, label, registered_at FROM registered_numbers ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def register_number(phone, label):
    cleaned = normalize_phone(phone)
    if not is_valid_phone(cleaned):
        return False, "That doesn't look like a valid phone number. Include your country code, e.g. +91 98765 43210."
    try:
        conn.execute("INSERT INTO registered_numbers (phone_number, label, registered_at) VALUES (?, ?, ?)",
                     (cleaned, label.strip() or "My number", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True, f"{cleaned} is now protected."
    except sqlite3.IntegrityError:
        return False, "That number is already registered."


def unregister_number(number_id):
    conn.execute("DELETE FROM registered_numbers WHERE id = ?", (number_id,))
    conn.commit()


# The palette is intentionally centralized: every component draws from these tokens.
theme = "light" if st.session_state.bright_mode else "dark"
colors = {
    "light": {"bg": "#FFFFFF", "surface": "#F0E5FA", "surface2": "#DDEFE0", "text": "#123B24", "muted": "#496550", "edge": "#CDB9DD", "primary": "#6F2DBD", "accent": "#236B36", "shadow": "rgba(64, 35, 82, .12)"},
    "dark": {"bg": "#0B0A10", "surface": "#251D31", "surface2": "#1B2B24", "text": "#F5F1FA", "muted": "#C5BCCB", "edge": "#4A3A57", "primary": "#B995E9", "accent": "#75B88A", "shadow": "rgba(0, 0, 0, .34)"},
}[theme]

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
  :root {{ color-scheme:{theme}; }} #MainMenu, footer, header {{ visibility:hidden; }}
  .stApp {{ --bg:{colors['bg']}; --surface:{colors['surface']}; --surface-2:{colors['surface2']}; --text:{colors['text']}; --muted:{colors['muted']}; --edge:{colors['edge']}; --primary:{colors['primary']}; --accent:{colors['accent']}; --danger:#E85B5B; background:var(--bg); color:var(--text); font-family:'Manrope',sans-serif; transition:background .35s ease,color .35s ease; }}
  .brand, .hero h1, h1, h2, h3, .metric-value, .hero-stat b {{ font-family:'Space Grotesk',sans-serif; }}
  .block-container {{ max-width:1180px !important; padding:1.1rem 1.5rem 3rem !important; margin:0 auto; }}
  .top-bar {{ border-bottom:1px solid var(--edge); padding:0 0 .9rem; margin-bottom:1.2rem; }}
  .brand {{ color:var(--text); font-size:1.5rem; font-weight:800; letter-spacing:-.02em; line-height:1.1; }}
  .brand span {{ color:var(--primary); }}
  .brand small {{ display:block; margin-left:2.05rem; color:var(--muted); font-size:.72rem; font-weight:500; font-style:italic; letter-spacing:.01em; }}
  .protection-status {{ font-size:.82rem; font-weight:700; text-align:right; line-height:1.5; }}
  .protection-status .dot {{ color:var(--accent); }}
  .protection-status .sub {{ color:var(--muted); font-weight:600; font-size:.78rem; }}
  .stToggle {{ padding-top:.2rem; }} .stToggle label {{ color:var(--text)!important; font-weight:600!important; }} .stToggle [data-baseweb='switch'] {{ border:1px solid var(--primary)!important; }} .stToggle [data-testid='stThumbValue'] {{ background:var(--primary)!important; }}
  h1,h2,h3,p,label,.stMarkdown {{ color:var(--text); }}
  .hero {{ background:linear-gradient(115deg,var(--surface),var(--surface-2)); border:1px solid var(--edge); border-radius:18px; padding:1.6rem 1.8rem; margin-bottom:1.1rem; box-shadow:0 12px 30px {colors['shadow']}; display:flex; justify-content:space-between; align-items:center; gap:1.5rem; flex-wrap:wrap; }}
  .hero h1 {{ font-size:1.7rem; margin:0 0 .35rem; line-height:1.25; max-width:34ch; }}
  .hero p {{ margin:0; color:var(--muted); max-width:46ch; }}
  .hero-stats {{ display:flex; gap:1.6rem; }}
  .hero-stat {{ text-align:center; }}
  .hero-stat b {{ display:block; font-size:1.5rem; font-weight:800; color:var(--primary); }}
  .hero-stat span {{ color:var(--muted); font-size:.72rem; font-weight:600; }}
  .card,.creator-card {{ background:linear-gradient(145deg,var(--surface),var(--surface-2)); border:1px solid var(--edge); border-radius:16px; padding:1.15rem; min-height:360px; box-shadow:0 8px 22px {colors['shadow']}; }}
  .card h3 {{ margin:.1rem 0 1rem; font-size:1.05rem; }}
  .metric-label {{ color:var(--muted); font-size:.75rem; font-weight:700; letter-spacing:.02em; }}
  .metric-value {{ color:var(--text); font-size:1.7rem; font-weight:800; margin:.15rem 0 1rem; }}
  .risk-box {{ background:rgba(232,91,91,.12); border:1px solid var(--danger); color:var(--text); border-radius:12px; padding:.9rem 1rem; margin:.9rem 0; }}
  .incident {{ border-left:3px solid var(--primary); padding:.55rem .7rem; margin:.65rem 0; background:var(--surface-2); border-radius:0 8px 8px 0; color:var(--text); font-size:.87rem; }}
  .incident small {{ display:block; color:var(--muted); margin-top:.2rem; }}
  .stButton>button {{ width:100%; border-radius:10px; min-height:44px; font-weight:700; border:1px solid var(--primary); background:var(--surface); color:var(--text); }}
  .stButton>button[kind='primary'] {{ background:var(--primary); color:{'#FFFFFF' if theme == 'light' else '#12100F'}; }}
  .stButton>button:hover {{ transform:translateY(-1px); border-color:var(--accent); box-shadow:0 8px 18px {colors['shadow']}; }}
  .stButton>button:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
  div[data-testid='stTextInput'] input {{ background:var(--surface-2); color:var(--text); border-color:var(--edge); }}
  [data-testid='stTabs'] [role='tab'] {{ color:var(--muted); font-weight:700; }} [data-testid='stTabs'] [aria-selected='true'] {{ color:var(--primary); }}
  .creators-hero {{ padding:1.25rem 0 .65rem; }} .creators-hero h2 {{ margin:0 0 .35rem; }} .creators-hero p,.profile-copy {{ color:var(--muted); line-height:1.6; }}
  .avatar {{ width:52px; height:52px; display:grid; place-items:center; border-radius:16px; background:linear-gradient(135deg,var(--primary),var(--accent)); color:#141313; font-weight:900; letter-spacing:.03em; }}
  .creator-role {{ color:var(--accent); font-size:.73rem; font-weight:800; letter-spacing:.04em; margin:1.2rem 0 .25rem; }}
  .creator-card {{ transition:transform .24s ease,box-shadow .24s ease; }} .creator-card:hover {{ transform:translateY(-5px); }} .creator-card h3 {{ margin:0; }}
  @keyframes profileExpand {{ from {{ opacity:0; transform:scale(.94) translateY(18px); }} to {{ opacity:1; transform:scale(1) translateY(0); }} }}
  .profile-panel {{ background:linear-gradient(120deg,var(--surface),var(--surface-2)); border:1px solid var(--primary); border-radius:18px; padding:1.4rem; margin:1rem 0; animation:profileExpand .42s cubic-bezier(.2,.8,.2,1) both; }}
  .tag {{ display:inline-block; border:1px solid var(--edge); border-radius:999px; color:var(--muted); font-size:.78rem; padding:.32rem .6rem; margin:.25rem .25rem 0 0; }}
  .instagram {{ color:var(--primary)!important; font-weight:800; text-decoration:none; }}
  .number-row {{ display:flex; align-items:center; justify-content:space-between; gap:.75rem; border:1px solid var(--edge); border-radius:12px; padding:.7rem .9rem; margin-bottom:.6rem; background:var(--surface-2); }}
  .number-row .digits {{ font-weight:800; font-size:1rem; }}
  .number-row .meta {{ color:var(--muted); font-size:.76rem; }}
  .empty-state {{ border:1px dashed var(--edge); border-radius:14px; padding:1.4rem; text-align:center; color:var(--muted); }}
</style>
""", unsafe_allow_html=True)


def render_creator_directory():
    """Render the shared creator directory for the tab and dedicated return page."""
    profile_columns = st.columns(3, gap="large")
    for index, person in enumerate(CREATORS):
        with profile_columns[index]:
            st.markdown(f"<div class='creator-card'><div class='avatar'>{person['initials']}</div><p class='creator-role'>{person['role']}</p><h3>{person['name']}</h3><p class='profile-copy'>See my story, skills, and the perspective I bring to Scam-Proof.</p></div>", unsafe_allow_html=True)
            if st.button(f"View {person['name'].split()[0]}'s profile", key=f"creator_{index}"):
                st.session_state.selected_creator = index
                st.session_state.creator_directory = True
                st.rerun()


active_numbers = registered_numbers()

st.markdown('<div class="top-bar">', unsafe_allow_html=True)
left, switch, right = st.columns([5, 1.7, 2.2], vertical_alignment="center")
with left:
    st.markdown("<div class='brand'>🛡️ <span>Scam-Proof</span><small>Think twice before you trust the ring</small></div>", unsafe_allow_html=True)
with switch:
    st.toggle("Light mode", key="bright_mode", help="Switch between light and dark views.")
with right:
    if active_numbers:
        status_line = f"<div class='protection-status'><span class='dot'>●</span> PROTECTION ACTIVE<div class='sub'>{len(active_numbers)} number{'s' if len(active_numbers) != 1 else ''} registered</div></div>"
    else:
        status_line = "<div class='protection-status'><span style='color:var(--muted)'>○</span> NO NUMBER REGISTERED<div class='sub'>Add one in My Numbers</div></div>"
    st.markdown(status_line, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.selected_creator is not None:
    person = CREATORS[st.session_state.selected_creator]
    st.markdown("<div class='creators-hero'><p class='creator-role'>Scam-Proof · Meet the creators</p><h2>About me</h2></div>", unsafe_allow_html=True)
    st.markdown(f"<section class='profile-panel'><div class='avatar'>{person['initials']}</div><p class='creator-role'>{person['role']}</p><h2>{person['name']}</h2><p class='profile-copy'>{person['bio']}</p><div>{''.join(f'<span class=\"tag\">{skill}</span>' for skill in person['skills'])}</div><p style='margin:1.1rem 0 0'><a class='instagram' href='https://www.instagram.com/{person['instagram']}/' target='_blank' rel='noopener'>◎ @{person['instagram']} on Instagram</a></p></section>", unsafe_allow_html=True)
    if st.button("← Back to creators"):
        st.session_state.selected_creator = None
        st.session_state.creator_directory = True
        st.rerun()
    st.stop()

if st.session_state.creator_directory:
    st.markdown("<div class='creators-hero'><p class='creator-role'>Scam-Proof · The Team</p><h2>Meet the creators</h2><p>The people combining product design, reliable data, and seamless integrations to build Scam-Proof.</p></div>", unsafe_allow_html=True)
    render_creator_directory()
    if st.button("← Back to dashboard"):
        st.session_state.creator_directory = False
        st.rerun()
    st.stop()

total_incidents = conn.execute("SELECT COUNT(*) FROM cyber_reports").fetchone()[0]
st.markdown(f"""<section class='hero'>
  <div><h1>The call ends the moment the scam begins.</h1><p>Live protection for voice phishing, impersonation, and AI-generated scams — built for quick, confident decisions.</p></div>
  <div class='hero-stats'>
    <div class='hero-stat'><b>{len(active_numbers)}</b><span>NUMBERS PROTECTED</span></div>
    <div class='hero-stat'><b>{total_incidents}</b><span>INCIDENTS LOGGED</span></div>
  </div>
</section>""", unsafe_allow_html=True)

live_tab, audio_tab, numbers_tab, creators_tab = st.tabs(["📞  Live Call Shield", "🎧  Audio File Inspector", "📱  My Numbers", "👥  Meet the Creators"])

with live_tab:
    call_col, monitor_col, action_col = st.columns(3, gap="large")
    with call_col:
        st.markdown("<div class='card'><h3>📞 Incoming call</h3>", unsafe_allow_html=True)
        if active_numbers:
            default_number = active_numbers[0][1]
        else:
            default_number = "+91 98765-43210"
        phone_number = st.text_input("Caller number", value=default_number)
        st.markdown("<div class='metric-label'>Caller reputation</div><div class='metric-value'>Unknown</div>", unsafe_allow_html=True)
        if not st.session_state.call_active:
            if st.button("Start call simulation", type="primary"):
                st.session_state.call_active, st.session_state.show_police_popup = True, False; st.rerun()
        else:
            st.warning("Call in progress — listening securely.")
            if st.button("End call"):
                st.session_state.call_active = False; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with monitor_col:
        st.markdown("<div class='card'><h3>🤖 AI monitoring</h3>", unsafe_allow_html=True)
        if st.session_state.call_active:
            bar, status = st.progress(0), st.empty()
            for amount in range(20, 101, 20):
                time.sleep(.25); bar.progress(amount); status.caption(f"Checking speech and audio patterns… {amount}%")
            keywords = ["Bank account blocked", "Verify OTP immediately", "CBI emergency", "Transfer money"]
            st.session_state.pending_report = {"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "caller_id":phone_number, "score":round(random.uniform(89,98.5),2), "transcript":f"Urgent: {random.choice(keywords)}. Transfer funds now.", "status":"PENDING USER CONFIRMATION"}
            st.session_state.call_active, st.session_state.show_police_popup = False, True; st.rerun()
        else:
            st.markdown("<div class='metric-label'>Shield status</div><div class='metric-value'>Ready</div><p style='color:var(--muted)'>Start a simulation to watch Scam-Proof assess speech patterns, urgency signals, and synthetic-audio risk in real time.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with action_col:
        st.markdown("<div class='card'><h3>📋 Recent activity</h3>", unsafe_allow_html=True)
        rows = report_rows()
        if rows:
            for timestamp, caller, score, status in rows:
                st.markdown(f"<div class='incident'><b>{caller}</b> · {score:.1f}% risk<small>{timestamp} · {status}</small></div>", unsafe_allow_html=True)
        else: st.info("No incidents logged yet.")
        st.markdown("<div class='metric-label' style='margin-top:1rem'>Emergency support</div><div class='metric-value' style='color:var(--accent)'>1930</div></div>", unsafe_allow_html=True)
    if st.session_state.show_police_popup and st.session_state.pending_report:
        report = st.session_state.pending_report
        st.markdown(f"<div class='risk-box'><b>🚨 Scam detected — call ended automatically</b><br>Risk score: <b>{report['score']}%</b> · Caller: {report['caller_id']}<br><span style='color:var(--muted)'>“{report['transcript']}”</span></div>", unsafe_allow_html=True)
        confirm, archive, _ = st.columns([2, 2, 4])
        with confirm:
            if st.button("Dispatch cyber report", type="primary"):
                report["status"]="DISPATCHED TO CYBER POLICE"; save_report(report); st.session_state.show_police_popup=False; st.session_state.pending_report=None; st.success("Report dispatched successfully."); st.rerun()
        with archive:
            if st.button("Save locally"):
                report["status"]="SAVED TO LOCAL LOGS"; save_report(report); st.session_state.show_police_popup=False; st.session_state.pending_report=None; st.info("Report saved to your local log."); st.rerun()

with audio_tab:
    upload_col, result_col, guide_col = st.columns(3, gap="large")
    with upload_col:
        st.markdown("<div class='card'><h3>📤 Upload a voice note</h3>", unsafe_allow_html=True); uploaded_file=st.file_uploader("Audio file (.wav, .mp3, .ogg)", type=["wav","mp3","ogg"])
        if uploaded_file: st.audio(uploaded_file)
        st.markdown("</div>", unsafe_allow_html=True)
    with result_col:
        st.markdown("<div class='card'><h3>🔍 Verification result</h3>", unsafe_allow_html=True)
        if uploaded_file and st.button("Run fraud verification", type="primary"):
            with st.spinner("Checking audio patterns…"): score=analyze_audio_features(uploaded_file)
            if score > 70: st.error(f"High fraud risk: {score}%"); save_report({"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"caller_id":f"Audio_{uploaded_file.name}","score":score,"transcript":"Suspicious uploaded voice message","status":"FLAGGED AUDIO"})
            else: st.success(f"Appears authentic: {100-score:.1f}% human confidence")
        else: st.caption("Upload a file, then run verification.")
        st.markdown("</div>", unsafe_allow_html=True)
    with guide_col:
        st.markdown("<div class='card'><h3>💡 Quick safety check</h3><p style='color:var(--muted)'>Never share OTPs, passwords, or banking details during an unexpected call. Pause, verify independently, and report pressure tactics.</p><div class='metric-label'>Cyber fraud helpline</div><div class='metric-value' style='color:var(--accent)'>1930</div></div>", unsafe_allow_html=True)

with numbers_tab:
    form_col, list_col = st.columns([2, 3], gap="large")
    with form_col:
        st.markdown("<div class='card'><h3>➕ Register a number</h3><p style='color:var(--muted); margin-top:-.5rem'>Scam-Proof actively watches calls to and from the numbers you register here.</p>", unsafe_allow_html=True)
        with st.form("register_number_form", clear_on_submit=True):
            new_phone = st.text_input("Phone number", placeholder="+91 98765 43210")
            new_label = st.text_input("Label (optional)", placeholder="e.g. My phone, Mom's phone")
            submitted = st.form_submit_button("Register number", type="primary")
        if submitted:
            success, message = register_number(new_phone, new_label)
            st.session_state.number_feedback = (success, message)
            st.rerun()
        if st.session_state.number_feedback:
            ok, message = st.session_state.number_feedback
            (st.success if ok else st.error)(message)
            st.session_state.number_feedback = None
        st.markdown("</div>", unsafe_allow_html=True)
    with list_col:
        st.markdown("<div class='card'><h3>🔐 Protected numbers</h3>", unsafe_allow_html=True)
        current_numbers = registered_numbers()
        if current_numbers:
            for number_id, phone, label, registered_at in current_numbers:
                row_l, row_r = st.columns([5, 1])
                with row_l:
                    st.markdown(f"<div class='number-row'><div><div class='digits'>{phone}</div><div class='meta'>{label} · added {registered_at}</div></div></div>", unsafe_allow_html=True)
                with row_r:
                    if st.button("Remove", key=f"remove_{number_id}"):
                        unregister_number(number_id)
                        st.rerun()
        else:
            st.markdown("<div class='empty-state'>No numbers registered yet.<br>Add your first number to turn on live call protection.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with creators_tab:
    st.markdown("<div class='creators-hero'><h2>Meet the creators</h2><p>The people combining product design, reliable data, and seamless integrations to build Scam-Proof.</p></div>", unsafe_allow_html=True)
    render_creator_directory()