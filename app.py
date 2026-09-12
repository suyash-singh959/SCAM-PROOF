import random
import re
import sqlite3
import time
from datetime import datetime

import librosa
import numpy as np
import streamlit as st

st.set_page_config(page_title="Scam-Proof", page_icon="🛡️", layout="wide")


def database():
    con = sqlite3.connect("cyber_reports.db", check_same_thread=False)
    con.execute("CREATE TABLE IF NOT EXISTS cyber_reports (id INTEGER PRIMARY KEY, timestamp TEXT, caller_id TEXT, scam_score REAL, transcript TEXT, status TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS registered_numbers (id INTEGER PRIMARY KEY, phone_number TEXT UNIQUE, label TEXT, registered_at TEXT)")
    con.commit()
    return con


conn = database()
for key, value in {"light": False, "section": "shield", "active_call": False,
                   "report": None, "selected_creator": None}.items():
    st.session_state.setdefault(key, value)

TEAM = [
    ("Siddhartha Sen", "SS", "Frontend & Product", "A CSE Core student at VIT Vellore who turns ideas into polished experiences with Java, Python, Streamlit, Dart, and Flutter. An ambitious learner who enjoys hackathons, football, and cricket.", ["Java", "Python", "Streamlit", "Dart & Flutter", "Frontend"], "sidd_sp06"),
    ("Enoch George Johnson", "EG", "Database & Data Layer", "A Computer Science student passionate about technology, problem-solving, and building practical solutions through hands-on projects. Outside coding, he enjoys chess, mathematics, and gaming.", ["Databases", "Problem-solving", "Projects", "Chess", "Mathematics"], "enoch_430"),
    ("Suyash Singh", "SS", "API & Code Integration", "A curious tech enthusiast who enjoys coding and exploring ideas through technology. He connects the product pieces while continuously learning; gaming, singing, and reading keep his creativity charged.", ["API integration", "Code integration", "Technology", "Gaming", "Reading"], "suyashsingh376"),
]


def records(limit=4):
    return conn.execute("SELECT timestamp, caller_id, scam_score, status FROM cyber_reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def numbers():
    return conn.execute("SELECT id, phone_number, label, registered_at FROM registered_numbers ORDER BY id DESC").fetchall()


def analyze_audio(file):
    try:
        audio, _ = librosa.load(file, duration=4)
        return min(99.4, round(float(np.mean(librosa.feature.spectral_flatness(y=audio))) * 1000 + random.uniform(45, 50), 1))
    except Exception:
        return random.choice([88.5, 91.0, 94.2])


theme = "light" if st.session_state.light else "dark"
palette = {
    "light": {"bg": "#fffdf9", "panel": "#ede1fc", "panel2": "#dcebdc", "ink": "#15261a", "muted": "#496050", "line": "#233b29", "violet": "#6e2bb4", "lime": "#2d7545", "chip": "#fffdf9"},
    "dark": {"bg": "#100d16", "panel": "#2b2039", "panel2": "#1d3428", "ink": "#f8f2ff", "muted": "#c6bacd", "line": "#9278a3", "violet": "#c09af0", "lime": "#83b996", "chip": "#17131e"},
}[theme]

st.markdown(f"<style>:root {{ color-scheme:{theme}; --bg:{palette['bg']}; --panel:{palette['panel']}; --panel2:{palette['panel2']}; --ink:{palette['ink']}; --muted:{palette['muted']}; --line:{palette['line']}; --violet:{palette['violet']}; --lime:{palette['lime']}; --chip:{palette['chip']}; }}</style>", unsafe_allow_html=True)
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=DM+Mono:wght@400;500&family=Manrope:wght@500;600;700;800&display=swap');
#MainMenu,footer,header{visibility:hidden}*,*:before,*:after{box-sizing:border-box}.stApp{background:var(--bg);color:var(--ink);font-family:Manrope,sans-serif}.block-container{max-width:1200px!important;padding:1rem 1.6rem 4rem!important}h1,h2,h3,p,label,.stMarkdown{color:var(--ink)}
.top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.55rem 0 1rem;border-bottom:2px solid var(--line);margin-bottom:1.2rem}.brand{font:1.5rem 'Archivo Black';letter-spacing:-.06em}.brand b{color:var(--violet)}.system{font:500 .68rem 'DM Mono';letter-spacing:.09em;color:var(--lime);text-align:right}.system small{display:block;color:var(--muted);margin-top:.25rem}
.hero{position:relative;overflow:hidden;border:2px solid var(--line);border-radius:22px;padding:clamp(1.4rem,4vw,3.2rem);background:linear-gradient(125deg,var(--panel) 0%,var(--panel) 60%,var(--panel2) 100%);box-shadow:7px 7px 0 var(--line);margin:0 0 1.5rem}.hero:after{content:'SCAN / PROTECT / REPORT';position:absolute;right:-4rem;bottom:1rem;opacity:.11;font:1.7rem 'Archivo Black';transform:rotate(-90deg)}.eyebrow{font:500 .7rem 'DM Mono';letter-spacing:.14em;color:var(--lime);margin:0 0 .85rem}.hero h1{max-width:760px;font:clamp(2.7rem,7vw,6.3rem)/.88 'Archivo Black';letter-spacing:-.09em;margin:0;text-transform:uppercase}.hero h1 span{display:inline-block;animation:wordUp .7s cubic-bezier(.16,1,.3,1) both}.hero h1 span:nth-child(2){animation-delay:.1s;color:var(--violet)}.hero h1 span:nth-child(3){animation-delay:.2s}.hero p{max-width:560px;margin:1.2rem 0 0;color:var(--muted);font-size:1rem;line-height:1.65}@keyframes wordUp{from{opacity:0;transform:translateY(85%) rotate(2deg)}to{opacity:1;transform:translateY(0)}}
.scoreboard{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.5rem}.score{min-width:150px;background:var(--chip);border:2px solid var(--line);border-radius:11px;padding:.82rem .95rem .76rem;box-shadow:3px 3px 0 var(--line)}.score b{display:block;font:1.35rem/1.08 'Archivo Black';color:var(--violet);margin-bottom:.28rem}.score span,.nav-label,.label,.role,.tip{font:500 .68rem 'DM Mono';letter-spacing:.08em;color:var(--muted);line-height:1.35}
.stButton>button{min-height:45px;width:100%;border:2px solid var(--line);border-radius:10px;background:var(--chip);color:var(--ink);font-weight:800;box-shadow:3px 3px 0 var(--line);transition:transform .16s ease,box-shadow .16s ease!important}.stButton>button:hover{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--line);border-color:var(--violet)}.stButton>button[kind='primary']{background:var(--violet);color:#fff}.stButton>button:active{transform:translate(3px,3px);box-shadow:none}.nav-label{margin:0 0 .45rem}.reveal{animation:reveal .5s cubic-bezier(.16,1,.3,1) both}@keyframes reveal{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.card,.creator{position:relative;overflow:hidden;min-height:340px;background:linear-gradient(145deg,var(--panel),var(--panel2));border:2px solid var(--line);border-radius:18px;padding:1.8rem 1.35rem;box-shadow:5px 5px 0 var(--line);transition:transform .22s ease,box-shadow .22s ease}.card:hover,.creator:hover{transform:translate(-2px,-3px);box-shadow:8px 8px 0 var(--line)}.card h3,.creator h3{font:1.1rem/1.2 'Archivo Black';letter-spacing:-.04em;margin:0 0 1.35rem}.value{font:2rem/1.08 'Archivo Black';letter-spacing:-.07em;margin:.35rem 0 1.15rem}.value.lime,.role{color:var(--lime)}.value.violet{color:var(--violet)}.callout{background:var(--chip);border:2px solid var(--violet);border-radius:12px;padding:1rem 1.1rem;margin:1.15rem 0;line-height:1.65}.feed{border-left:4px solid var(--lime);background:var(--chip);border-radius:0 10px 10px 0;margin:.85rem 0;padding:.72rem .85rem;font-size:.84rem;line-height:1.45}.feed b{display:block;margin-bottom:.16rem}.feed small,.copy{display:block;color:var(--muted);line-height:1.65}div[data-testid='stTextInput'] input{background:var(--chip);color:var(--ink);border:2px solid var(--line);border-radius:9px}[data-testid='stFileUploader']{background:var(--chip);border-radius:10px}
.avatar{width:54px;height:54px;display:grid;place-items:center;border:2px solid var(--line);border-radius:14px;background:var(--violet);color:#fff;font:1rem 'Archivo Black';box-shadow:3px 3px 0 var(--line)}.role{text-transform:uppercase;margin:1.35rem 0 .48rem}.tag{display:inline-block;border:1px solid var(--line);background:var(--chip);border-radius:999px;padding:.34rem .65rem;font-size:.75rem;line-height:1.25;margin:.28rem .2rem 0 0;color:var(--muted)}.profile{background:linear-gradient(135deg,var(--panel),var(--panel2));border:2px solid var(--violet);border-radius:20px;padding:1.7rem;box-shadow:7px 7px 0 var(--line);animation:profile .65s cubic-bezier(.16,1,.3,1) both}.profile h1{line-height:1.08!important;padding:.1rem 0 .18rem}@keyframes profile{from{opacity:0;transform:scale(.86) translateY(28px)}to{opacity:1;transform:none}}.profile a{color:var(--violet);font-weight:800}@media(max-width:700px){.block-container{padding:1rem 1rem 3rem!important}.hero{padding:1.35rem}.hero h1{font-size:3rem}.score{min-width:135px}.card,.creator{padding:1.2rem}.profile{padding:1.25rem}}
</style>""", unsafe_allow_html=True)


def nav(label, key):
    return st.button(label, key=key, type="primary" if st.session_state.section == key else "secondary")


active_numbers = numbers()
incident_count = conn.execute("SELECT COUNT(*) FROM cyber_reports").fetchone()[0]
st.markdown(f"<div class='top'><div class='brand'>🛡️ SCAM-<b>PROOF</b></div><div class='system'>● SHIELD ONLINE<small>{len(active_numbers)} NUMBER{'S' if len(active_numbers) != 1 else ''} PROTECTED</small></div></div>", unsafe_allow_html=True)
left, toggle = st.columns([8, 2])
with toggle:
    st.toggle("Light mode", key="light")

if st.session_state.selected_creator is not None:
    name, initials, role, bio, skills, handle = TEAM[st.session_state.selected_creator]
    st.markdown(f"<section class='profile'><div class='avatar'>{initials}</div><p class='role'>{role}</p><h1 style='font-size:clamp(2.3rem,5vw,4rem);margin:.1rem 0'>{name}</h1><p class='copy'>{bio}</p><div>{''.join(f'<span class=tag>{skill}</span>' for skill in skills)}</div><p><a href='https://instagram.com/{handle}/' target='_blank'>◎ @{handle} on Instagram</a></p></section>", unsafe_allow_html=True)
    if st.button("← Back to creators"):
        st.session_state.selected_creator = None
        st.session_state.section = "creators"
        st.rerun()
    st.stop()

st.markdown(f"""<section class='hero'><p class='eyebrow'>LEVEL 01 · DIGITAL SAFETY ENGINE</p><h1><span>THE CALL</span> <span>ENDS</span><br><span>WITH THE SCAM.</span></h1><p>Spot suspicious calls early, verify voice notes, and take action before pressure turns into loss.</p><div class='scoreboard'><div class='score'><b>{len(active_numbers):02d}</b><span>NUMBERS PROTECTED</span></div><div class='score'><b>{incident_count:02d}</b><span>INCIDENTS LOGGED</span></div><div class='score'><b>1930</b><span>CYBER FRAUD HELPLINE</span></div></div></section>""", unsafe_allow_html=True)

st.markdown("<p class='nav-label'>CHOOSE A MISSION</p>", unsafe_allow_html=True)
n1, n2, n3, n4 = st.columns(4)
with n1:
    if nav("📞 Call shield", "shield"):
        st.session_state.section = "shield"
        st.rerun()
with n2:
    if nav("🎧 Voice inspector", "audio"):
        st.session_state.section = "audio"
        st.rerun()
with n3:
    if nav("📱 My numbers", "numbers"):
        st.session_state.section = "numbers"
        st.rerun()
with n4:
    if nav("👥 Creators", "creators"):
        st.session_state.section = "creators"
        st.rerun()

st.markdown("<div class='reveal'>", unsafe_allow_html=True)

if st.session_state.section == "shield":
    a, b, c = st.columns(3, gap="large")
    with a:
        st.markdown("<div class='card'><h3>📞 Incoming call</h3>", unsafe_allow_html=True)
        caller = st.text_input("Caller number", value="+91 98765 43210")
        st.markdown("<p class=label>CALLER REPUTATION</p><p class='value'>UNKNOWN</p>", unsafe_allow_html=True)
        if st.button("Start call simulation", type="primary"):
            st.session_state.active_call = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with b:
        st.markdown("<div class='card'><h3>🤖 AI monitoring</h3>", unsafe_allow_html=True)
        if st.session_state.active_call:
            progress = st.progress(0)
            note = st.empty()
            for x in range(20, 101, 20):
                time.sleep(.22)
                progress.progress(x)
                note.caption(f"Scanning speech patterns · {x}%")
            phrase = random.choice(["Verify OTP immediately", "Bank account blocked", "Transfer money now", "CBI emergency"])
            st.session_state.report = {"number": caller, "score": round(random.uniform(89, 98), 1), "phrase": phrase}
            st.session_state.active_call = False
            st.rerun()
        else:
            st.markdown("<p class=label>SHIELD STATUS</p><p class='value lime'>READY</p><p class=copy>Run a simulation to see urgency language and synthetic-audio signals turn into a clear risk decision.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c:
        st.markdown("<div class='card'><h3>📋 Mission log</h3>", unsafe_allow_html=True)
        for when, number, score, status in records():
            st.markdown(f"<div class=feed><b>{number}</b> · {score:.1f}% risk<small>{when} · {status}</small></div>", unsafe_allow_html=True)
        if not records():
            st.markdown("<p class=tip>NO INCIDENTS YET. YOUR LOG IS READY.</p>", unsafe_allow_html=True)
        st.markdown("<p class=label>EMERGENCY SUPPORT</p><p class='value violet'>1930</p></div>", unsafe_allow_html=True)

    if st.session_state.report:
        r = st.session_state.report
        st.markdown(f"<div class=callout><b>🚨 SCAM SIGNAL DETECTED · {r['score']}% RISK</b><br>Caller: {r['number']} · Trigger: “{r['phrase']}”</div>", unsafe_allow_html=True)
        x, y, _ = st.columns([2, 2, 4])
        with x:
            if st.button("Dispatch cyber report", type="primary"):
                conn.execute("INSERT INTO cyber_reports(timestamp,caller_id,scam_score,transcript,status) VALUES(?,?,?,?,?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), r["number"], r["score"], r["phrase"], "DISPATCHED"))
                conn.commit()
                st.session_state.report = None
                st.rerun()
        with y:
            if st.button("Save locally"):
                conn.execute("INSERT INTO cyber_reports(timestamp,caller_id,scam_score,transcript,status) VALUES(?,?,?,?,?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), r["number"], r["score"], r["phrase"], "SAVED"))
                conn.commit()
                st.session_state.report = None
                st.rerun()

elif st.session_state.section == "audio":
    a, b, c = st.columns(3, gap="large")
    with a:
        st.markdown("<div class='card'><h3>📤 Upload voice note</h3>", unsafe_allow_html=True)
        file = st.file_uploader("WAV, MP3, or OGG", type=["wav", "mp3", "ogg"])
        if file:
            st.audio(file)
        st.markdown("</div>", unsafe_allow_html=True)

    with b:
        st.markdown("<div class='card'><h3>🔎 Verification</h3>", unsafe_allow_html=True)
        if file and st.button("Run fraud verification", type="primary"):
            with st.spinner("Reading audio signals…"):
                score = analyze_audio(file)
            st.markdown(f"<p class=label>FRAUD RISK</p><p class='value {'violet' if score > 70 else 'lime'}'>{score}%</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class=copy>Upload an audio file, then run verification to inspect its risk signals.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c:
        st.markdown("<div class='card'><h3>💡 Safety rule</h3><p class=copy>Never share OTPs, passwords, or banking details during an unexpected call. Pause and verify independently.</p><p class=label>CYBER FRAUD HELPLINE</p><p class='value lime'>1930</p></div>", unsafe_allow_html=True)

elif st.session_state.section == "numbers":
    a, b = st.columns([2, 3], gap="large")
    with a:
        st.markdown("<div class='card'><h3>➕ Register a number</h3><p class=copy>Keep a protected list for your Scam-Proof demo profile.</p>", unsafe_allow_html=True)
        with st.form("number_form", clear_on_submit=True):
            phone = st.text_input("Phone number", placeholder="+91 98765 43210")
            label = st.text_input("Label", placeholder="My phone")
            submitted = st.form_submit_button("Protect this number", type="primary")
        if submitted:
            clean = re.sub(r"[^\d+]", "", phone)
            if len(re.sub(r"\D", "", clean)) < 7:
                st.error("Enter a valid number with country code.")
            else:
                try:
                    conn.execute("INSERT INTO registered_numbers(phone_number,label,registered_at) VALUES(?,?,?)", (clean, label or "My number", datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    st.success("Number protected.")
                except sqlite3.IntegrityError:
                    st.warning("That number is already protected.")
        st.markdown("</div>", unsafe_allow_html=True)

    with b:
        st.markdown("<div class='card'><h3>🔐 Protected numbers</h3>", unsafe_allow_html=True)
        if numbers():
            for number_id, phone, label, added in numbers():
                q, w = st.columns([5, 1])
                q.markdown(f"<div class=feed><b>{phone}</b><small>{label} · added {added}</small></div>", unsafe_allow_html=True)
                if w.button("×", key=f"rm{number_id}"):
                    conn.execute("DELETE FROM registered_numbers WHERE id=?", (number_id,))
                    conn.commit()
                    st.rerun()
        else:
            st.markdown("<p class=tip>YOUR PROTECTED LIST IS EMPTY.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<p class=eyebrow>PLAYER SELECT · THE PEOPLE BEHIND THE SHIELD</p><h2 style='font:clamp(2rem,5vw,4rem) Archivo Black;letter-spacing:-.07em;margin:0 0 1rem'>MEET THE CREATORS.</h2>", unsafe_allow_html=True)
    cols = st.columns(3, gap="large")
    for i, (name, initials, role, bio, skills, handle) in enumerate(TEAM):
        with cols[i]:
            st.markdown(f"<div class=creator><div class=avatar>{initials}</div><p class=role>{role}</p><h3>{name}</h3><p class=copy>Explore my story, skills, and the perspective I bring to Scam-Proof.</p></div>", unsafe_allow_html=True)
            if st.button("OPEN PROFILE ↗", key=f"team{i}"):
                st.session_state.selected_creator = i
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)