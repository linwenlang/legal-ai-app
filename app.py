import streamlit as st
from openai import OpenAI
import json
import os
import pandas as pd
from io import BytesIO
import docx

# 1. 页面配置：手机端适配与标题
st.set_page_config(page_title="律盾 AI - 专业法务助手", page_icon="⚖️", layout="wide")

# --- 数据库持久化 ---
USER_DB_FILE = "users_data.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    # 默认超级管理员
    return {"admin": {"password": "888", "role": "admin", "count": 999}}

def save_users(users_data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)

if 'users' not in st.session_state:
    st.session_state.users = load_users()

# 2. API 配置 (从 Streamlit Secrets 读取)
try:
    client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")
except Exception as e:
    st.error("❌ API 密钥未配置或错误，请检查 Secrets 设置。")
    st.stop()

# --- 工具函数：导出 Word ---
def text_to_docx(text):
    doc = docx.Document()
    doc.add_heading('律盾 AI - 专业法务报告', 0)
    for line in text.split('\n'):
        if line.strip(): 
            doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# 3. 侧边栏：登录/注册与客服
with st.sidebar:
    st.title("🛡️ 律盾 AI 会员中心")
    if "logged_in" not in st.session_state: 
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        t1, t2 = st.tabs(["🔑 登录", "📝 手机注册"])
        with t1:
            u = st.text_input("手机号", key="l_u")
            p = st.text_input("密码", type="password", key="l_p")
            if st.button("立即进入", use_container_width=True):
                if u in st.session_state.users and st.session_state.users[u]["password"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = st.session_state.users[u].get("role", "user")
                    st.rerun()
                else: st.error("❌ 账号或密码错误")
        with t2:
            st.caption("🎁 新用户注册送 5 次专业额度")
            ru = st.text_input("📱 手机号", placeholder="11位手机号", key="r_u")
            rp = st.text_input("🔒 设置密码", type="password", key="r_p")
            promo = st.text_input("🎟️ 邀请码 (选填)", value="VIP888")
            if st.button("完成注册", use_container_width=True):
                if len(ru) == 11 and rp:
                    if ru not in st.session_state.users:
                        st.session_state.users[ru] = {"password": rp, "role": "user", "count": 5, "promo": promo}
                        save_users(st.session_state.users)
                        st.success("✅ 注册成功！请切换到登录页")
                    else: st.error("❌ 手机号已存在")
                else: st.warning("请输入完整的手机号和密码")
        st.stop()
    else:
        # --- 已登录：显示额度与客服 ---
        st.success(f"👤 欢迎：{st.session_state.user}")
        curr_user = st.session_state.users[st.session_state.user]
        st.metric("剩余法务额度", f"{curr_user['count']} 次")
        
        # 👑 管理员后台
        if st.session_state.role == "admin":
            st.divider()
            with st.expander("👑 管理员控制面板"):
                df = pd.DataFrame.from_dict(st.session_state.users, orient='index')
                st.dataframe(df[['count', 'promo']])
                target = st.selectbox("充值对象", list(st.session_state.users.keys()))
                num = st.number_input("充值点数", 1, 500, 20)
                if st.button("确认充值"):
                    st.session_state.users[target]["count"] += num
                    save_users(st.session_state.users)
                    st.success(f"已为 {target} 充值 {num} 次")
                    st.rerun()
        
        # 🛠️ 客服板块
        st.divider()
        st.info(f"🆘 额度充值/合作咨询：\n\n微信：**linwlang12**")
        st.caption("推广福利：每邀请一人额外赠送 5 次")

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# 4. 主界面
st.title("⚖️ 律盾 AI - 您的移动私人律师")

# 拦截逻辑
def check_credit():
    if st.session_state.users[st.session_state.user]["count"] > 0:
        return True
    else:
        st.error("⚠️ 您的剩余额度为 0 ！无法执行此操作。")
        st.warning("💡 请添加客服微信 **linwlang12** 获取更多额度。")
        return False

def use_credit():
    st.session_state.users[st.session_state.user]["count"] -= 1
    save_users(st.session_state.users)

mode = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 专业翻译"])

# --- 风险排雷 ---
with mode[0]:
    st.subheader("🎯 合同风险深度扫描")
    c1, c2, c3 = st.columns(3)
    t_scan = ""
    if c1.button("⚖️ 霸王条款分析"): t_scan = "霸王条款与免责"
    if c2.button("💰 支付结算风险"): t_scan = "付款期限与逾期责任"
    if c3.button("📝 劳动合同风险"): t_scan = "试用期与社保合规"
    
    txt = st.text_area("请粘贴合同内容：", height=200, key="audit_area")
    if st.button("🚀 执行全方位深度扫描", use_container_width=True) or t_scan:
        if txt and check_credit():
            with st.spinner("AI 律师审阅中..."):
                target = t_scan if t_scan else "全面风险"
                prompt = f"作为资深律师，请针对以下内容进行【{target}】分析。请先提供详尽的中文报告，然后加上分隔符'---SPLIT---'，最后提供简要的英文版分析摘要。"
                try:
                    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":prompt},{"role":"user","content":txt}])
                    ans = res.choices[0].message.content
                    if "---SPLIT---" in ans:
                        cn, en = ans.split("---SPLIT---")
                        cl, cr = st.columns(2)
                        with cl: st.error("🇨🇳 中文分析建议"); st.write(cn)
                        with cr: st.warning("🇺🇸 English Summary"); st.write(en)
                        st.divider()
                        d1, d2 = st.columns(2)
                        d1.download_button("📥 下载中文 Word 报告", data=text_to_docx(cn), file_name="风险分析报告.docx")
                        d2.download_button("📥 下载完整对照文档", data=text_to_docx(ans.replace("---SPLIT---","\n")), file_name="完整对照.docx")
                        use_credit()
                    else:
                        st.info(ans)
                        use_credit()
                except Exception as e:
                    st.error(f"分析出错：{e}")

# --- 智能起草 ---
with mode[1]:
    st.subheader("✍️ 法律文书起草")
    req = st.text_area("您的起草要求：", placeholder="例如：起草一份租房合同，要求租金押一付三，不得转租...", height=200)
    if st.button("✨ 立即生成专业文书", use_container_width=True):
        if req and check_credit():
            with st.spinner("起草中..."):
                try:
                    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"你是一位专业的中国执业律师，请起草文案。"},{"role":"user","content":req}])
                    ans = res.choices[0].message.content
                    st.info(ans)
                    st.download_button("📥 下载 Word 文稿", data=text_to_docx(ans), file_name="文书起草.docx")
                    use_credit()
                except Exception as e: st.error(f"失败：{e}")

# --- 专业翻译 ---
with mode[2]:
    st.subheader("🌐 法律专业翻译")
    tin = st.text_area("请粘贴原文：", height=200, placeholder="支持中英互译...")
    if st.button("🚀 开始极速翻译", use_container_width=True):
        if tin and check_credit():
            with st.spinner("专业翻译中..."):
                try:
                    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role":"system","content":"你是一位法律专业翻译官，请确保术语准确严谨。"},{"role":"user","content":tin}])
                    ans = res.choices[0].message.content
                    st.success(ans)
                    st.download_button("📥 下载翻译文档", data=text_to_docx(ans), file_name="法律翻译.docx")
                    use_credit()
                except Exception as e: st.error(f"失败：{e}")
