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
    return {"admin": {"password": "888", "count": 10}}

def save_u(d):
    with open(USER_DB, "w") as f: json.dump(d, f)

if 'u' not in st.session_state: st.session_state.u = load_u()

# 3. 初始化 AI
client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")

# 4. 侧边栏：登录与注册
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    if "in" not in st.session_state: st.session_state["in"] = False
    
    if not st.session_state["in"]:
        tab_login, tab_reg = st.tabs(["登录", "注册"])
        with tab_login:
            uid = st.text_input("账号")
            pwd = st.text_input("密码", type="password")
            if st.button("立即登录"):
                if uid in st.session_state.u and st.session_state.u[uid]["password"] == pwd:
                    st.session_state["in"], st.session_state.cur = True, uid
                    st.rerun()
                else: st.error("账号或密码错误")
        with tab_reg:
            new_uid = st.text_input("设置账号")
            new_pwd = st.text_input("设置密码", type="password")
            if st.button("提交注册"):
                if new_uid and new_pwd:
                    if new_uid in st.session_state.u: st.error("账号已存在")
                    else:
                        st.session_state.u[new_uid] = {"password": new_pwd, "count": 5}
                        save_u(st.session_state.u)
                        st.success("注册成功！请切换到登录页")
                else: st.warning("请填写完整")
        st.stop()
    else:
        st.success(f"欢迎：{st.session_state.cur}")
        st.write(f"剩余额度：{st.session_state.u[st.session_state.cur]['count']}次")
        st.info("充值联系微信：\n**linwlang12**")
        if st.button("退出登录"):
            st.session_state["in"] = False
            st.rerun()

# 5. 主功能区
st.title("⚖️ 律盾 AI 律师专业版")
m = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 中英翻译"])

# 通用处理逻辑（含下载）
def run_ai(prompt_type, input_text, key_prefix):
    if st.button(f"执行{prompt_type}", key=f"btn_{key_prefix}"):
        if not input_text:
            st.warning("内容不能为空")
            return
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            with st.spinner("AI 律师正在处理..."):
                try:
                    r = client.chat.completions.create(
                        model="deepseek-chat", 
                        messages=[{"role":"user","content": f"请以专业律师身份进行{prompt_type}：{input_text}"}]
                    )
                    res = r.choices[0].message.content
                    st.markdown("### 📋 处理结果")
                    st.write(res)
                    # 扣费
                    st.session_state.u[st.session_state.cur]['count'] -= 1
                    save_u(st.session_state.u)
                    # 下载功能
                    st.download_button(label="📥 下载结果为 TXT", data=res, file_name=f"{prompt_type}结果.txt", mime="text/plain")
                except Exception as e: st.error(f"出错：{e}")
        else: st.error("额度不足，请联系客服")

with m[0]:
    t0 = st.text_area("粘贴合同/条款：", height=200, key="t0")
    run_ai("风险分析", t0, "0")

with m[1]:
    t1 = st.text_area("输入起草要求：", height=200, key="t1")
    run_ai("文书起草", t1, "1")

with m[2]:
    t2 = st.text_area("粘贴需要翻译的法律文本：", height=200, key="t2")
    run_ai("中英互译", t2, "2")
