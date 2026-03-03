import streamlit as st
from openai import OpenAI
import json
import os
import pandas as pd
from io import BytesIO
import docx

# 1. 页面配置：完全汉化标题和图标
st.set_page_config(
    page_title="律盾 AI", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 汉化 Streamlit 默认菜单（可选） ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 用户数据管理 ---
USER_DB_FILE = "users_data.json"
def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"admin": {"password": "888", "role": "admin", "count": 999}}

def save_users(users_data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

if 'users' not in st.session_state:
    st.session_state.users = load_users()

# 2. API 配置
try:
    client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")
except:
    st.error("❌ 未检测到 API 配置，请在后台设置。")
    st.stop()

def text_to_docx(text):
    doc = docx.Document()
    for line in text.split('\n'):
        if line.strip(): doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 侧边栏：全中文登录与客服
with st.sidebar:
    st.title("🛡️ 会员中心")
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        t1, t2 = st.tabs(["🔑 立即登录", "📝 免费注册"])
        with t1:
            u = st.text_input("手机号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("进入系统"):
                if u in st.session_state.users and st.session_state.users[u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = st.session_state.users[u].get("role", "user")
                    st.rerun()
                else: st.error("账号或密码错误")
        with t2:
            st.caption("🎁 注册即赠送 5 次专业额度")
            ru = st.text_input("📱 手机号", placeholder="11位手机号", key="r_u")
            rp = st.text_input("🔒 设置密码", type="password", key="r_p")
            promo = st.text_input("🎟️ 邀请码", value="VIP888")
            if st.button("提交注册"):
                if len(ru) == 11 and rp and promo == "VIP888":
                    if ru not in st.session_state.users:
                        st.session_state.users[ru] = {"password": rp, "role": "user", "count": 5, "promo": promo}
                        save_users(st.session_state.users)
                        st.success("注册成功！请切换至登录页")
                    else: st.error("该账号已注册")
        st.stop()
    else:
        st.success(f"👤 您好：{st.session_state.user}")
        curr = st.session_state.users[st.session_state.user]
        st.metric("剩余额度", f"{curr['count']} 次")
        
        if st.session_state.role == "admin":
            if st.checkbox("👑 管理员后台"):
                df = pd.DataFrame.from_dict(st.session_state.users, orient='index')
                st.dataframe(df[['count', 'promo']])
                target = st.selectbox("充值账号", list(st.session_state.users.keys()))
                num = st.number_input("充值数量", 1, 500, 20)
                if st.button("确认充值"):
                    st.session_state.users[target]["count"] += num
                    save_users(st.session_state.users)
                    st.rerun()
        
        st.divider()
        with st.expander("💬 充值中心", expanded=True):
            st.info("充值咨询微信：\n**linwlang12**")
        
        if st.button("🚪 退出登录"):
            st.session_state.logged_in = False
            st.rerun()

# 4. 主界面：汉化核心模块
st.title("⚖️ 律盾 AI - 您的 24h 私人律师")

def check():
    if st.session_state.users[st.session_state.user]["count"] > 0: return True
    st.error("⚠️ 余额不足，无法执行！")
    st.warning("请添加客服微信：**linwlang12** 充值额度")
    return False

def use():
    st.session_state.users[st.session_state.user]["count"] -= 1
    save_users(st.session_state.users)

mode = st.selectbox("核心功能切换：", ["🔍 智能风险排雷", "✍️ 法律文书起草", "🌐 专业翻译"])

if mode == "🔍 智能风险排雷":
    st.write("---")
    txt = st.text_area("请粘贴合同内容：", height=250, placeholder="粘贴内容后点击下方按钮...")
    if st.button("🚀 开始深度扫描") and txt:
        if check():
            with st.spinner("AI 律师正在审阅..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"资深律师，请进行法律排雷，指出风险并给出修改建议。"},{"role":"user","content":txt}])
                st.markdown("### 📋 排雷分析报告")
                st.write(res.choices[0].message.content)
                use(); st.rerun()

elif mode == "✍️ 法律文书起草":
    st.write("---")
    req = st.text_area("您的起草要求：", height=150, placeholder="例如：起草一份租房合同，要求押一付三...")
    if st.button("✨ 立即生成文书") and req:
        if check():
            with st.spinner("文书起草中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"专业律师，起草严谨的法律文书。"},{"role":"user","content":req}])
                st.info("### 📄 合同草案生成成功")
                st.write(res.choices[0].message.content)
                st.download_button("📥 下载 Word 文档", data=text_to_docx(res.choices[0].message.content), file_name="文书草案.docx")
                use(); st.rerun()

else:
    st.write("---")
    tin = st.text_area("翻译文本：", height=250, placeholder="粘贴需要翻译的法律内容...")
    if st.button("🚀 极速翻译") and tin:
        if check():
            with st.spinner("翻译中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"法律翻译官。"},{"role":"user","content":tin}])
                st.success("### 📜 翻译结果")
                st.write(res.choices[0].message.content)
                use(); st.rerun()