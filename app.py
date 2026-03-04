import streamlit as st
from openai import OpenAI
import json, os

# 1. 页面配置
st.set_page_config(page_title="律盾 AI", page_icon="⚖️", layout="wide")

# 2. 数据库逻辑
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

# 3. 初始化 AI (DeepSeek)
client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")

# 4. 侧边栏：登录系统
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    if "in" not in st.session_state: st.session_state["in"] = False
    if not st.session_state["in"]:
        uid = st.text_input("账号/手机号")
        pwd = st.text_input("密码", type="password")
        if st.button("立即登录"):
            if uid in st.session_state.u and st.session_state.u[uid]["password"] == pwd:
                st.session_state["in"], st.session_state.cur = True, uid
                st.rerun()
            else: st.error("账号或密码错误")
        st.stop()
    else:
        st.success(f"欢迎：{st.session_state.cur}")
        st.write(f"剩余额度：{st.session_state.u[st.session_state.cur]['count']}次")
        st.divider()
        st.info("充值客服微信：\n**linwlang12**")
        if st.button("退出登录"):
            st.session_state["in"] = False
            st.rerun()

# 5. 主功能区
st.title("⚖️ 律盾 AI 律师")
m = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 专业翻译"])

for i, (name, prompt) in enumerate([("分析：", "分析风险："), ("起草：", "起草文书："), ("翻译：", "法律翻译：")]):
    with m[i]:
        txt = st.text_area("请输入内容：", key=f"t{i}", height=200)
        if st.button(f"确认执行", key=f"b{i}"):
            if st.session_state.u[st.session_state.cur]['count'] > 0:
                with st.spinner("AI 律师思考中..."):
                    r = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"user","content":prompt+txt}])
                    st.write(r.choices[0].message.content)
                    st.session_state.u[st.session_state.cur]['count'] -= 1
                    save_u(st.session_state.u)
            else: st.error("额度不足，请联系客服")
