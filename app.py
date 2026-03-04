import streamlit as st
from openai import OpenAI
import json
import os
import pandas as pd
from io import BytesIO
import docx

# 1. 页面配置
st.set_page_config(page_title="律盾 AI - 专业法务助手", page_icon="⚖️", layout="wide")

# --- 数据库持久化 ---
USER_DB_FILE = "users_data.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
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
    st.error("❌ API 配置错误，请检查 Secrets。")
    st.stop()

# --- 工具函数 ---
def text_to_docx(text):
    doc = docx.Document()
    for line in text.split('\n'):
        if line.strip(): doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 侧边栏：登录与客服中心
with st.sidebar:
    st.title("🛡️ 律盾 AI 会员中心")
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        t1, t2 = st.tabs(["🔑 登录", "📝 注册"])
        with t1:
            u = st.text_input("手机号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("立即进入"):
                if u in st.session_state.users and st.session_state.users[u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = st.session_state.users[u].get("role", "user")
                    st.rerun()
                else: st.error("账号或密码错误")
        with t2:
            st.caption("🎁 注册即送 5 次专业额度")
            ru = st.text_input("📱 手机号", placeholder="11位手机号", key="r_u")
            rp = st.text_input("🔒 设置密码", type="password", key="r_p")
            promo = st.text_input("🎟️ 邀请码", value="VIP888")
            if st.button("完成注册"):
                if len(ru) == 11 and rp and promo == "VIP888":
                    if ru not in st.session_state.users:
                        st.session_state.users[ru] = {"password": rp, "role": "user", "count": 5, "promo": promo}
                        save_users(st.session_state.users)
                        st.success("注册成功！请登录")
                    else: st.error("账号已存在")
        st.stop()
    else:
        # --- 已登录状态 ---
        st.success(f"👤 用户：{st.session_state.user}")
        curr_user = st.session_state.users[st.session_state.user]
        st.metric("剩余法务额度", f"{curr_user['count']} 次")
        
        # 👑 管理员后台
        if st.session_state.role == "admin":
            st.divider()
            if st.checkbox("👑 管理员控制台"):
                df = pd.DataFrame.from_dict(st.session_state.users, orient='index')
                st.dataframe(df[['count', 'promo']])
                target = st.selectbox("充值对象", list(st.session_state.users.keys()))
                num = st.number_input("充值点数", 1, 500, 20)
                if st.button("确认充值"):
                    st.session_state.users[target]["count"] += num
                    save_users(st.session_state.users)
                    st.rerun()
        
        # 🛠️ 客服与充值中心（新增侧边栏常驻板块）
        st.divider()
        with st.expander("💬 客服与充值中心", expanded=True):
            st.write("如需获取更多次数或遇到问题：")
            st.info("官方客服微信：\n**linwlang12**")
            st.caption("长按上方微信号即可复制")
            st.write("---")
            st.caption("提示：公测期间充值立享 5 折优惠")

        if st.button("🚪 退出登录"):
            st.session_state.logged_in = False
            st.rerun()

# 4. 主界面核心逻辑
st.title("⚖️ 律盾 AI - 您的移动私人律师")

# 🔴 核心：拦截逻辑（带红色报错提示）
def check_credit():
    if st.session_state.users[st.session_state.user]["count"] > 0:
        return True
    else:
        # 这里是你要的红色显眼报错框
        st.error("⚠️ 您的剩余额度为 0 ！无法执行此操作。")
        st.warning("💡 请联系客服微信：**linwlang12** 进行人工充值。")
        return False

def use_credit():
    st.session_state.users[st.session_state.user]["count"] -= 1
    save_users(st.session_state.users)

mode = st.selectbox("功能切换：", ["🔍 风险排雷", "✍️ 智能起草", "🌐 专业翻译"])

# --- 模块：风险排雷 ---
if mode == "🔍 风险排雷":
    st.subheader("🎯 专项风险扫描")
    c1, c2, c3 = st.columns(3)
    t_scan = ""
    if c1.button("⚖️ 霸王条款"): t_scan = "霸王条款与免责"
    if c2.button("💰 支付风险"): t_scan = "付款期限与逾期责任"
    if c3.button("📝 劳动权益"): t_scan = "试用期与社保合规"
    
    txt = st.text_area("粘贴文本：", height=250)
    if (t_scan or st.button("🚀 执行全方位深度扫描")) and txt:
        if check_credit():  # 拦截检查
            with st.spinner("律师审查中..."):
                target = t_scan if t_scan else "全面风险"
                prompt = f"针对内容执行【{target}】分析。先中文，再'---SPLIT---'，最后英文。"
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":prompt},{"role":"user","content":txt}])
                ans = res.choices[0].message.content
                if "---SPLIT---" in ans:
                    cn, en = ans.split("---SPLIT---")
                    cl, cr = st.columns(2)
                    with cl: st.error("🇨🇳 中文建议"); st.write(cn)
                    with cr: st.warning("🇺🇸 英文分析"); st.write(en)
                    st.divider()
                    d1, d2 = st.columns(2)
                    d1.download_button("📥 下载中文报告", data=text_to_docx(cn), file_name="中文建议.docx")
                    d2.download_button("📥 下载对照报告", data=text_to_docx(ans.replace("---SPLIT---","\n")), file_name="对照报告.docx")
                use_credit() # 成功执行后扣费
                st.rerun()

# --- 模块：智能起草 ---
elif mode == "✍️ 智能起草":
    req = st.text_area("您的起草要求：", placeholder="例如：上海租房合同，押一付三...")
    if st.button("✨ 立即生成文书"):
        if req and check_credit(): # 拦截检查
            with st.spinner("起草中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"专业律师。"},{"role":"user","content":req}])
                ans = res.choices[0].message.content
                st.info(ans)
                st.download_button("📥 下载 Word 文档", data=text_to_docx(ans), file_name="文书草案.docx")
                use_credit()
                st.rerun()

# --- 模块：专业翻译 ---
else:
    tin = st.text_area("翻译文本：", height=250)
    if st.button("🚀 开始翻译"):
        if tin and check_credit(): # 拦截检查
            with st.spinner("翻译中..."):
                res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"法律翻译，严谨。"},{"role":"user","content":tin}])
                ans = res.choices[0].message.content
                st.success(ans)
                st.download_button("📥 下载译文", data=text_to_docx(ans), file_name="译文.docx")
                use_credit()
                st.rerun()
