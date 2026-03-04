import streamlit as st
from openai import OpenAI
import json, os

# 1. 页面基本配置
st.set_page_config(page_title="律盾 AI", page_icon="⚖️", layout="wide")

# 2. 简易数据库：管理用户账号和剩余额度
USER_DB = "users.json"

def load_data():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f:
                return json.load(f)
        except:
            pass
    # 默认账号：账号 admin 密码 888 (额度 999 次)
    return {"admin": {"password": "888", "count": 999}}

def save_data(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f)

# 初始化数据到 Session
if 'db' not in st.session_state:
    st.session_state.db = load_data()

# 3. 初始化 OpenAI 客户端 (使用 DeepSeek 引擎)
client = OpenAI(
    api_key=st.secrets["api_key"], 
    base_url="https://api.deepseek.com"
)

# 4. 侧边栏：会员中心与登录系统
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    
    if "is_login" not in st.session_state:
        st.session_state.is_login = False
    
    if not st.session_state.is_login:
        st.subheader("请登录以使用专业功能")
        user_input = st.text_input("手机号/账号")
        pass_input = st.text_input("登录密码", type="password")
        if st.button("立即登录"):
            if user_input in st.session_state.db and st.session_state.db[user_input]["password"] == pass_input:
                st.session_state.is_login = True
                st.session_state.current_user = user_input
                st.rerun()
            else:
                st.error("❌ 账号或密码不正确")
        st.stop()  # 未登录状态下不显示主界面
    else:
        st.success(f"已登录：{st.session_state.current_user}")
        count = st.session_state.db[st.session_state.current_user]["count"]
        st.metric("剩余可用额度", f"{count} 次")
        st.divider()
        st.info(f"客服微信：**linwlang12**\n\n(额度不足请联系充值)")
        if st.button("安全退出"):
            st.session_state.is_login = False
            st.rerun()

# 5. 主功能界面
st.title("⚖️ 律盾 AI 律师")
st.markdown("---")

# 创建功能标签页
t1, t2, t3 = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 专业翻译"])

# --- 风险排雷 ---
with t1:
    content = st.text_area("请粘贴需要分析的合同或法律条文：", height=200, key="audit")
    if st.button("开始 AI 分析"):
        if st.session_state.db[st.session_state.current_user]["count"] > 0:
            if content:
                with st.spinner("AI 律师正在审阅..."):
                    try:
                        resp = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role":"user","content":"请作为法律专家分析以下文本的法律风险并给出专业建议："+content}]
                        )
                        st.markdown("### 📝 分析建议")
                        st.write(resp.choices[0].message.content)
                        # 扣除额度
                        st.session_state.db[st.session_state.current_user]["count"] -= 1
                        save_data(st.session_state.db)
                    except Exception as e:
                        st.error(f"连接失败：{e}")
            else:
                st.warning("请输入文本内容")
        else:
            st.error("额度不足，请联系客服充值")

# --- 智能起草 ---
with t2:
    draft_req = st.text_area("输入您的文书起草要求（如：一份租赁合同）：", key="draft")
    if st.button("立即起草"):
        if st.session_state.db[st.session_state.current_user]["count"] > 0:
            if draft_req:
                with st.spinner("正在生成专业文书..."):
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role":"user","content":"请起草一份专业的法律文书："+draft_req}]
                    )
                    st.info(resp.choices[0].message.content)
                    st.session_state.db[st.session_state.current_user]["count"] -= 1
                    save_data(st.session_state.db)
            else:
                st.warning("请输入起草要求")
        else:
            st.error("额度不足")

# --- 专业翻译 ---
with t3:
    trans_text = st.text_area("粘贴法律文本进行中英互译：", key="trans")
    if st.button("执行翻译"):
        if st.session_state.db[st.session_state.current_user]["count"] > 0:
            if trans_text:
                with st.spinner("翻译中..."):
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role":"user","content":"法律专业翻译（中英）："+trans_text}]
                    )
                    st.success(resp.choices[0].message.content)
                    st.session_state.db[st.session_state.current_user]["count"] -= 1
                    save_data(st.session_state.db)
