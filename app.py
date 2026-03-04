import streamlit as st
from openai import OpenAI
import json
import os
import pandas as pd
from io import BytesIO
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 1. 页面配置
st.set_page_config(page_title="律盾 AI - 专业法务助手", page_icon="⚖️", layout="wide")

# 自定义 CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #ffffff; border-radius: 5px; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 数据库持久化 ---
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
except Exception as e:
    st.error("❌ API 配置失效，请检查后台 Secrets。")
    st.stop()

# --- 工具函数：生成 Word 报告 ---
def generate_pro_docx(title, content):
    doc = docx.Document()
    header = doc.add_heading(title, 0)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line in content.split('\n'):
        if line.strip():
            p = doc.add_paragraph(line)
            run = p.add_run()
            run.font.size = Pt(11)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 侧边栏：登录与上帝视角后台
with st.sidebar:
    st.title("🛡️ 会员管理中心")
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        t1, t2 = st.tabs(["🔑 登录", "📝 手机注册"])
        with t1:
            u = st.text_input("手机号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("立即进入系统", use_container_width=True):
                if u in st.session_state.users and st.session_state.users[u]["password"] == p:
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.session_state.role = st.session_state.users[u].get("role", "user")
                    st.rerun()
                else: st.error("❌ 验证失败")
        with t2:
            st.caption("🎁 新用户注册立赠 5 次额度")
            ru = st.text_input("📱 手机号", key="r_u")
            rp = st.text_input("🔒 设置密码", type="password", key="r_p")
            if st.button("完成注册并领取额度", use_container_width=True):
                if len(ru) == 11 and rp:
                    if ru not in st.session_state.users:
                        st.session_state.users[ru] = {"password": rp, "role": "user", "count": 5}
                        save_users(st.session_state.users)
                        st.success("✅ 注册成功！请登录")
                    else: st.error("❌ 账号已存在")
        st.stop()
    else:
        st.success(f"👤 已认证：{st.session_state.user}")
        curr_u = st.session_state.users[st.session_state.user]
        st.metric("剩余可用点数", f"{curr_u['count']} 次")
        
        # 👑 管理员上帝视角后台 (支持加减点数)
        if st.session_state.role == "admin":
            st.divider()
            with st.expander("👑 超级管理员后台 (加减/修改)"):
                st.write("📊 用户数据全览")
                df = pd.DataFrame.from_dict(st.session_state.users, orient='index')
                if not df.empty:
                    st.dataframe(df[['password', 'count']], use_container_width=True)
                
                st.divider()
                target = st.selectbox("选择账号", list(st.session_state.users.keys()))
                op_mode = st.radio("操作模式", ["增加额度", "扣除额度", "直接重置为"], horizontal=True)
                num = st.number_input("点数", 1, 1000, 10)
                
                if st.button("确认修改用户信息"):
                    if op_mode == "增加额度":
                        st.session_state.users[target]["count"] += num
                    elif op_mode == "扣除额度":
                        st.session_state.users[target]["count"] -= num
                    else:
                        st.session_state.users[target]["count"] = num
                    
                    save_users(st.session_state.users)
                    st.success(f"✅ 已完成对 {target} 的{op_mode}操作")
                    st.rerun()

        st.divider()
        st.info("🆘 客服微信：**linwlang12**")
        if st.button("🚪 安全退出", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# 4. 主界面核心功能
st.title("⚖️ 律盾 AI - 专业私人律师旗舰版")

def check_and_use():
    if st.session_state.users[st.session_state.user]["count"] <= 0:
        st.error("⚠️ 余额不足！请添加客服微信 **linwlang12** 充值获取更多额度。")
        return False
    return True

tabs = st.tabs(["🔍 合同风险排雷", "✍️ 专业文书起草", "🌐 法律文本翻译"])

# --- 模块 1：高级风险分析 ---
with tabs[0]:
    st.subheader("🎯 风险评估与条款审查")
    txt = st.text_area("请粘贴合同内容：", height=250, key="audit_in")
    opt = st.radio("扫描深度", ["标准扫描", "深度挖掘（含法律依据）", "霸王条款专项"], horizontal=True)
    is_en = st.checkbox("生成双语对照报告")

    if st.button("🚀 执行专家级审计", use_container_width=True):
        if txt and check_and_use():
            with st.spinner("⚖️ 律师团队审查中..."):
                prompt = f"你是一位资深中国律师。请执行【{opt}】分析。必须包含风险评级、核心风险点、法律依据和修改建议。"
                if is_en: prompt += " 请先提供中文分析，再用 '---SPLIT---' 分隔，最后提供英文摘要。"
                try:
                    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":prompt},{"role":"user","content":txt}])
                    ans = res.choices[0].message.content
                    if "---SPLIT---" in ans:
                        cn, en = ans.split("---SPLIT---")
                        st.error("🇨🇳 中文深度报告"); st.write(cn)
                        st.warning("🇺🇸 English Report"); st.write(en)
                    else:
                        st.info(ans)
                    st.download_button("📥 下载 Word 报告", data=generate_pro_docx("法律风险审计报告", ans.replace("---SPLIT---","\n")), file_name="风险分析报告.docx")
                    st.session_state.users[st.session_state.user]["count"] -= 1
                    save_users(st.session_state.users)
                except Exception as e: st.error(f"分析失败: {e}")

# --- 模块 2：专业起草 ---
with tabs[1]:
    st.subheader("✍️ 法律文书标准起草")
    req = st.text_area("起草需求：", placeholder="描述：类型、金额、责任等...", height=200)
    if st.button("✨ 生成法律文书", use_container_width=True):
        if req and check_and_use():
            with st.spinner("正在起草..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"严谨中国律师。"},{"role":"user","content":req}])
                ans = res.choices[0].message.content
                st.code(ans, language="markdown")
                st.download_button("📥 下载 Word 文稿", data=generate_pro_docx("文书起草", ans), file_name="起草文书.docx")
                st.session_state.users[st.session_state.user]["count"] -= 1
                save_users(st.session_state.users)

# --- 模块 3：法律翻译 ---
with tabs[2]:
    st.subheader("🌐 国际法律术语翻译")
    tin = st.text_area("待翻译文本：", height=200)
    if st.button("🛰️ 执行专业翻译", use_container_width=True):
        if tin and check_and_use():
            with st.spinner("翻译中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"法律翻译专家。"},{"role":"user","content":tin}])
                ans = res.choices[0].message.content
                st.success(ans)
                st.download_button("📥 下载翻译件", data=generate_pro_docx("法律翻译报告", ans), file_name="翻译结果.docx")
                st.session_state.users[st.session_state.user]["count"] -= 1
                save_users(st.session_state.users)
