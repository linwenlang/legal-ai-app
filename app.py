import streamlit as st
from openai import OpenAI
import json, os

# 1. 页面基本配置
st.set_page_config(page_title="律盾 AI - 专业法律服务", page_icon="⚖️", layout="wide")

# 2. 数据库逻辑 (用户信息与额度)
USER_DB = "users.json"
def load_data():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, "r") as f: return json.load(f)
        except: pass
    # 默认管理员：账号 admin 密码 888
    return {"admin": {"password": "888", "count": 999}}

def save_data(data):
    with open(USER_DB, "w") as f: json.dump(data, f)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# 3. AI 客户端配置
client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")

# 4. 侧边栏：手机注册、登录与推广
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    
    if "is_login" not in st.session_state:
        st.session_state.is_login = False
    
    if not st.session_state.is_login:
        tab_login, tab_reg = st.tabs(["📲 手机登录", "🆕 快速注册"])
        
        with tab_login:
            u_log = st.text_input("手机号/账号", key="log_u")
            p_log = st.text_input("登录密码", type="password", key="log_p")
            if st.button("立即登录", use_container_width=True):
                if u_log in st.session_state.db and st.session_state.db[u_log]["password"] == p_log:
                    st.session_state.is_login = True
                    st.session_state.current_user = u_log
                    st.rerun()
                else: st.error("账号或密码错误")
        
        with tab_reg:
            u_reg = st.text_input("输入手机号", key="reg_u")
            p_reg = st.text_input("设置密码", type="password", key="reg_p")
            p_reg_confirm = st.text_input("确认密码", type="password", key="reg_pc")
            if st.button("完成注册", use_container_width=True):
                if len(u_reg) < 11: st.error("请输入正确的手机号")
                elif p_reg != p_reg_confirm: st.error("两次密码输入不一致")
                elif u_reg in st.session_state.db: st.error("该手机号已注册")
                else:
                    st.session_state.db[u_reg] = {"password": p_reg, "count": 3} # 注册送3次
                    save_data(st.session_state.db)
                    st.success("注册成功！请切换到登录页")
        
        st.divider()
        st.warning("🎁 推广福利：分享本站给好友，截图发给客服可额外获得 10 次额度！")
        st.stop()
    else:
        st.success(f"欢迎使用：{st.session_state.current_user}")
        st.metric("剩余可用额度", f"{st.session_state.db[st.session_state.current_user]['count']} 次")
        st.divider()
        st.info(f"🆘 额度充值/合作咨询：\n\n微信：**linwlang12**")
        if st.button("退出登录"):
            st.session_state.is_login = False
            st.rerun()

# 5. 主界面：核心功能区
st.title("⚖️ 律盾 AI 律师专业版")
st.markdown("---")

tabs = st.tabs(["🔍 风险排雷", "✍️ 智能起草", "🌐 中英翻译", "📢 推广中心"])

# 通用 AI 执行函数
def execute_legal_task(task_name, user_input, prompt_detail):
    if st.button(f"立即执行{task_name}", use_container_width=True):
        if not user_input:
            st.warning("⚠️ 请先输入需要处理的内容")
            return
        
        if st.session_state.db[st.session_state.current_user]["count"] > 0:
            with st.spinner(f"AI 律师正在为您进行{task_name}..."):
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": f"请以专业律师身份，完成以下{task_name}任务：{prompt_detail}\n\n内容如下：\n{user_input}"}]
                    )
                    result = response.choices[0].message.content
                    st.markdown("### 📋 处理结果")
                    st.write(result)
                    
                    # 扣除额度并保存
                    st.session_state.db[st.session_state.current_user]["count"] -= 1
                    save_data(st.session_state.db)
                    
                    # 下载功能
                    st.download_button(
                        label="📥 下载本次分析报告 (TXT)",
                        data=result,
                        file_name=f"律盾AI_{task_name}结果.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"处理失败，请稍后再试或联系客服。错误信息：{e}")
        else:
            st.error("❌ 您的额度已用完，请联系微信 linwlang12 充值")

with tabs[0]:
    st.subheader("合同法律风险排雷")
    t0 = st.text_area("请粘贴合同条款或协议内容：", height=250, placeholder="例如：粘贴一份租房合同，AI将为您分析其中的不公平条款...")
    execute_legal_task("风险分析", t0, "分析其中的法律风险、潜在陷阱并给出专业的修改建议。")

with tabs[1]:
    st.subheader("智能法律文书起草")
    t1 = st.text_area("请描述您的起草需求：", height=250, placeholder="例如：起草一份合伙开店协议，要求约定利润平分，一方负责经营，一方负责出资...")
    execute_legal_task("文书起草", t1, "根据要求起草一份逻辑严密、表述专业的法律文书。")

with tabs[2]:
    st.subheader("专业法律中英互译")
    t2 = st.text_area("请粘贴需要翻译的法律文本：", height=250, placeholder="支持中译英或英译中，AI将提供最准确的法律专业词汇翻译...")
    execute_legal_task("中英翻译", t2, "请提供精准的法律专业翻译，确保术语准确，语义严谨。")

with tabs[3]:
    st.subheader("推广与奖励")
    st.info("您的专属推广链接（长按复制）：")
    st.code(f"https://legal-ai-app.streamlit.app/\n快来试试这个超好用的AI律师助手！")
    st.write("📈 **推广说明：**")
    st.write("1. 每成功邀请一位好友注册，您可获得 5 次额度奖励。")
    st.write("2. 好友首充，您可获得 20% 的现金返现或双倍额度。")
    st.write("请将您的推广记录截图发送给微信：**linwlang12** 领取奖励。")
