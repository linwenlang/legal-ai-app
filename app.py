import streamlit as st
from openai import OpenAI
import json, os

# 1. 基础页面配置
st.set_page_config(page_title="律盾 AI", page_icon="⚖️", layout="wide")

# 2. 用户数据库管理 (保存在本地 users.json)
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f:
                return json.load(f)
        except:
            pass
    # 默认账号配置 (手机号: admin, 密码: 888)
    return {"admin": {"password": "888", "count": 999}}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

# 初始化 session 状态
if 'u' not in st.session_state:
    st.session_state.u = load_users()

# 3. 初始化 AI 客户端
# 提醒：必须在 Streamlit Secrets 里填好 api_key
client = OpenAI(
    api_key=st.secrets["api_key"], 
    base_url="https://api.deepseek.com"
)

# 4. 侧边栏：登录控制与客服
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    if "in" not in st.session_state:
        st.session_state["in"] = False
    
    if not st.session_state["in"]:
        st.subheader("请先登录")
        uid = st.text_input("账号/手机号")
        pwd = st.text_input("登录密码", type="password")
        if st.button("立即登录"):
            if uid in st.session_state.u and st.session_state.u[uid]["password"] == pwd:
                st.session_state["in"] = True
                st.session_state.cur = uid
                st.rerun()
            else:
                st.error("❌ 账号或密码错误")
        st.stop()  # 未登录则停止运行后续代码
    else:
        st.success(f"✅ 欢迎回来，{st.session_state.cur}")
        st.write(f"📊 剩余额度：**{st.session_state.u[st.session_state.cur]['count']}** 次")
        st.divider()
        st.info(f"💡 额度不足？请联系客服：\n\n微信：**linwlang12**")
        if st.button("退出登录"):
            st.session_state["in"] = False
            st.rerun()

# 5. 主功能界面 (只有登录后才会显示)
st.title("⚖️ 律盾 AI 专业法律助手")
st.caption("由 DeepSeek 强力驱动 | 您的专属智能法律顾问")

# 定义功能标签页
tabs = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 专业翻译"])

# --- 功能 1：风险排雷 ---
with tabs[0]:
    st.subheader("合同/法律文本分析")
    txt = st.text_area("请粘贴需要审阅的内容：", height=200, key="audit_input")
    if st.button("🚀 开始风险分析"):
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            if txt:
                with st.spinner("AI 律师正在深度审阅中..."):
                    try:
                        r = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role":"user","content":"请作为资深律师分析以下法律文本的潜在风险、陷阱并给出中文建议："+txt}]
                        )
                        st.markdown("### 📜 分析报告")
                        st.write(r.choices[0].message.content)
                        # 扣费并保存
                        st.session_state.u[st.session_state.cur]['count'] -= 1
                        save_users(st.session_state.u)
                    except Exception as e:
                        st.error(f"分析失败: {e}")
            else:
                st.warning("⚠️ 请先输入文本内容")
        else:
            st.error("❌ 余额不足，请联系客服充值")

# --- 功能 2：智能起草 ---
with tabs[1]:
    st.subheader("法律文书一键生成")
    req = st.text_area("请描述起草要求（例如：合伙协议，需包含利润平分）：", key="draft_input")
    if st.button("✨ 立即起草文书"):
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            if req:
                with st.spinner("正在生成专业文书..."):
                    try:
                        r = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role":"user","content":"请起草一份专业的中文法律文书，内容需严谨且符合法律规范："+req}]
                        )
                        st.success("✅ 生成成功！")
                        st.info(r.choices[0].message.content)
                        # 扣费
                        st.session_state.u[st.session_state.cur]['count'] -= 1
                        save_users(st.session_state.u)
                    except Exception as e:
                        st.error(f"生成失败: {e}")
            else:
                st.warning("⚠️ 请先输入起草要求")
        else:
            st.error("❌ 余额不足，请联系客服")

# --- 功能 3：专业翻译 ---
with tabs[2]:
    st.subheader("法律英语/中文互译")
    trs = st.text_area("粘贴法律文本进行专业翻译：", key="trans_input")
    if st.button("🌐 开始翻译"):
        if st.session_state.u[st.session_state.cur]['count'] > 0:
            if trs:
                with st.spinner("正在进行专业翻译..."):
                    try:
                        r = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role":"user","content":"请将以下内容进行法律专业的精准互译（中英）："+trs}]
                        )
                        st.markdown("### 🌍 翻译结果")
                        st.success(r.choices[0].message.content)
                        # 扣费
                        st.session_state.u[st.session_state.cur]['count'] -= 1
                        save_users(st.session_state.u)
                    except Exception as e:
                        st.error(f"翻译失败: {e}")
            else:
                st.warning("⚠️ 请先输入文本")
        else:
            st.error("❌ 余额不足，请联系客服")
