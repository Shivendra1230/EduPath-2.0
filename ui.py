import streamlit as st
from pathlib import Path

PAGES = ["01 Command Center","02 Profile","03 Evidence","04 Skill Map","05 Study Path","06 Practice Lab","07 Adaptive Loop","08 Interview Coach","09 Career Copilot","10 Progress", "11 Learning Library"]

def css():
    st.markdown("""<style>
    .stApp{background:#050d18;color:#f5f8fc}
    .block-container{max-width:1440px;padding:18px 28px 90px}
    .brand{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;border:1px solid #24425e;border-radius:22px;background:linear-gradient(110deg,#0b1c30,#081421);box-shadow:0 12px 38px #0005;margin-bottom:10px}
    .brand-left{display:flex;align-items:center;gap:15px}.logo{width:58px;height:58px;border-radius:18px;background:linear-gradient(135deg,#5eead4,#7c3aed);display:grid;place-items:center;color:#06101b;font-weight:900;font-size:27px}.brand-title{font-size:30px;font-weight:900;letter-spacing:-1.5px}.brand-sub{font-size:10px;letter-spacing:3px;color:#6f8aa4}.live{color:#5eead4;font-size:12px}
    [data-testid="stNavigation"]{background:#091727;border:1px solid #203a54;border-radius:17px;padding:6px;margin:10px 0 22px;overflow-x:auto}
    [data-testid="stNavigation"] a{border-radius:11px!important;padding:9px 12px!important;white-space:nowrap!important;font-size:13px!important}
    [data-testid="stNavigation"] a[aria-current="page"]{background:#12314a!important;color:#5eead4!important}
    h1,h2,h3{letter-spacing:-.5px}
    div[data-testid="stStatusWidget"]{border-radius:12px}
    .stAlert{border-radius:13px}
    @media(max-width:800px){
      .block-container{padding:12px 14px 60px}
      .brand{padding:14px 16px;border-radius:17px}
      .logo{width:44px;height:44px;border-radius:13px;font-size:22px}
      .brand-title{font-size:25px}
      .brand-sub{font-size:8px;letter-spacing:1.5px}
      .hero{padding:24px 22px;border-radius:18px}
      .hero h1{font-size:34px;letter-spacing:-1.5px}
    }
    .hero{border:1px solid #244762;border-radius:25px;padding:36px 40px;background:radial-gradient(circle at 90% 20%,#113b42,#0b1c30 48%,#081523);margin-bottom:22px}
    .kicker{color:#5eead4;font-size:10px;font-weight:900;letter-spacing:2.3px}.hero h1{font-size:46px;line-height:1.02;letter-spacing:-2.4px;margin:10px 0 12px}.hero p{color:#9db4ca;font-size:16px;max-width:920px}
    .card{background:#0b1a2a;border:1px solid #213b55;border-radius:17px;padding:20px}.metric{font-size:31px;font-weight:900}.muted{color:#8da5bc;font-size:13px}.section{font-size:26px;font-weight:850;margin:30px 0 10px}.pill{display:inline-block;border:1px solid #31516e;background:#10253a;color:#9fc0d6;border-radius:999px;padding:4px 9px;font-size:11px;margin-right:4px}
    div.stButton>button{border-radius:12px;border:1px solid #2a4b68;background:#10243a;color:#f6f8fb;font-weight:750;min-height:44px}div.stButton>button:hover{border-color:#5eead4;color:#5eead4}
    div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-testid="stNumberInput"] input,div[data-baseweb="select"]{background:#0b1929!important;color:#f5f8fb!important;border-color:#29455f!important}
    [data-testid="stChatMessage"]{border:1px solid #203b56;border-radius:15px;background:#091827}
    .chat-source{font-size:11px;color:#6f8da7;margin-top:7px}.success-box{border:1px solid #1e665f;background:#0a2928;padding:13px 16px;border-radius:13px}
    </style>""",unsafe_allow_html=True)

def header(live):
    st.markdown(f"""<div class="brand"><div class="brand-left"><div class="logo">E</div><div><div class="brand-title">EduPath</div><div class="brand-sub">ADAPTIVE CAREER INTELLIGENCE</div></div></div><div class="live">● {'GROQ LIVE' if live else 'LOCAL ANALYSIS'} · LANGGRAPH</div></div>""",unsafe_allow_html=True)

def hero(kicker,title,desc):
    st.markdown(f'<div class="hero"><div class="kicker">{kicker}</div><h1>{title}</h1><p>{desc}</p></div>',unsafe_allow_html=True)

def metric(title,value,sub):
    st.markdown(f'<div class="card"><div class="muted">{title}</div><div class="metric">{value}</div><div class="muted">{sub}</div></div>',unsafe_allow_html=True)
