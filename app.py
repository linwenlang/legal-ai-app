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
st.set_page_config(page_title="律盾 AI", page_icon="⚖️", layout="wide")

# --- APK 专属沉浸式美化插件 (关键：隐藏网页痕迹) ---
st.markdown("""
    <style>
    /* 隐藏顶部彩虹条、菜单按钮和底部水印 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 极致沉浸感：消除顶部空白 */
    .stApp { margin-top: -80px; }
    
    /* 统一商务色调与标签页美化 */
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] { 
        height: 45px; 
        background-color: #ffffff; 
        border-radius: 8px 8px 0 0;
        border: 1px solid #f0f0f0;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1E3A8A !important; 
        color: white !important; 
        font-weight: bold;
    }
    
    /* 隐藏滚动条让界面更清爽 */
    ::-webkit-scrollbar { width: 0px; background: transparent; }
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
except:
    st.error("❌ API 配置异常")
    st.stop()

# --- 工具函数：生成 Word ---
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

# 3. 侧边栏
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
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
        
        # 👑 管理员上帝视角后台
        if st.session_state.role == "admin":
            st.divider()
            with st.expander("👑 超级管理员后台"):
                df = pd.DataFrame.from_dict(st.session_state.users, orient='index')
                if not df.empty:
                    st.dataframe(df[['password', 'count']], use_container_width=True)
                
                st.divider()
                target = st.selectbox("选择账号", list(st.session_state.users.keys()))
                op_mode = st.radio("操作", ["增加额度", "扣除额度", "直接重置"], horizontal=True)
                num = st.number_input("数量", 1, 1000, 10)
                
                if st.button("确认修改"):
                    if op_mode == "增加额度": st.session_state.users[target]["count"] += num
                    elif op_mode == "扣除额度": st.session_state.users[target]["count"] -= num
                    else: st.session_state.users[target]["count"] = num
                    save_users(st.session_state.users)
                    st.success("✅ 操作成功")
                    st.rerun()

        st.divider()
        st.info("🆘 客服微信：**linwlang12**")
        if st.button("🚪 安全退出", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# 4. 主界面
st.title("⚖️ 律盾 AI 律师")

def check_and_use():
    if st.session_state.users[st.session_state.user]["count"] <= 0:
        st.error("⚠️ 余额不足！请联系微信 **linwlang12** 充值。")
        return False
    return True

tabs = st.tabs(["🔍 风险分析", "✍️ 文书起草", "🌐 翻译专家"])

with tabs[0]:
    txt = st.text_area("粘贴合同：", height=200, key="audit_in")
    opt = st.radio("深度", ["标准", "深度", "霸王条款"], horizontal=True)
    is_en = st.checkbox("中英双语报告")
    if st.button("🚀 执行审计", use_container_width=True):
        if txt and check_and_use():
            with st.spinner("审查中..."):
                prompt = f"资深律师分析【{opt}】。中英对照开关：{is_en}。需含法律依据。"
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":prompt},{"role":"user","content":txt}])
                ans = res.choices[0].message.content
                st.info(ans)
                st.download_button("📥 下载 Word", data=generate_pro_docx("审计报告", ans), file_name="分析报告.docx")
                st.session_state.users[st.session_state.user]["count"] -= 1
                save_users(st.session_state.users)

with tabs[1]:
    req = st.text_area("起草需求：", height=200)
    if st.button("✨ 立即生成", use_container_width=True):
        if req and check_and_use():
            with st.spinner("起草中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"专业律师。"},{"role":"user","content":req}])
                ans = res.choices[0].message.content
                st.write(ans)
                st.download_button("📥 下载文件", data=generate_pro_docx("文书草案", ans), file_name="起草结果.docx")
                st.session_state.users[st.session_state.user]["count"] -= 1
                save_users(st.session_state.users)

with tabs[2]:
    tin = st.text_area("翻译内容：", height=200)
    if st.button("🛰️ 专业翻译", use_container_width=True):
        if tin and check_and_use():
            with st.spinner("翻译中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"法律翻译。"},{"role":"user","content":tin}])
                ans = res.choices[0].message.content
                st.success(ans)
                st.download_button("📥 下载译文", data=generate_pro_docx("翻译报告", ans), file_name="翻译结果.docx")
                st.session_state.users[st.session_state.user]["count"] -= 1
                save_users(st.session_state.users)
