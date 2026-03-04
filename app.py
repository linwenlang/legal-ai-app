import streamlit as st
from openai import OpenAI
import json, os

# 1. 基础配置
st.set_page_config(page_title="律盾 AI", page_icon="⚖️", layout="wide")

# 2. 数据库简单化 (自动生成用户文件)
USER_DB = "users.json"
def load_u():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f: return json.load(f)
        except: pass
    return {"admin": {"password": "888", "count": 999}}

def save_u(d):
    with open(USER_DB, "w") as f: json.dump(d, f)

if 'u' not in st.session_state: st.session_state.u = load_u()

# 3. API 客户端
client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")

# 4. 侧边栏：登录与客服
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    if "in" not in st.session_state: st.session_state["in"] = False
    
    if not st.session_state["in"]:
        uid = st.text_input("手机号")
        pwd = st.text_input("密码", type="password")
        if st.button("立即登录"):
            if uid in st.session_state.u and st.session_state.u[uid]["password"] == pwd:
                st.session_state["in"] = True
                st.session_state.cur = uid
                st.rerun()
            else: st.error("账号或密码错误")
        st.stop()
    else:
        st.success(f"欢迎，{st.session_state.cur}")
        st.write(f"剩余额度：{st.session_state.u[st.session_state.cur]['count']}次")
        st.divider()
        st.info("充值客服微信：\n**linwlang12**")
        if st.button("退出登录"):
            st.session_state["in"] = False
            st.rerun()

# 5. 主功能区
st.title("⚖️ 律盾 AI 律师")
m = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 专业翻译"])

with m[0]:
    txt = st.text_area("粘贴需要分析的合同内容：", height=200, key="t1")
    if st.button("开始分析") and txt:
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            with st.spinner("AI 律师审阅中..."):
                r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"user","content":"请作为资深律师分析风险并给出中文建议："+txt}])
                st.write(r.choices[0].message.content)
                st.session_state.u[st.session_state.cur]['count'] -= 1
                save_u(st.session_state.u)
        else: st.error("额度不足，请联系客服")

with m[1]:
    req = st.text_area("输入起草要求：", key="t2")
    if st.button("立即起草") and req:
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            with st.spinner("生成中..."):
                r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"user","content":"请起草一份专业的中文法律文书："+req}])
                st.info(r.choices[0].message.content)
                st.session_state.u[st.session_state.cur]['count'] -= 1
                save_u(st.session_state.u)

with m[2]:
    trs = st.text_area("粘贴法律内容进行翻译：", key="t3")
    if st.button("极速翻译") and trs:
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            with st.spinner("翻译中..."):
                r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"user","content":"法律专业中英翻译："+trs}])
                st.success(r.choices[0].message.content)
                st.session_state.u[st.session_state.cur]['count'] -= 1
                save_u(st.session_state.u)