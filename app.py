import streamlit as st
from openai import OpenAI

# 基础配置
st.set_page_config(page_title="律盾 AI", page_icon="⚖️", layout="wide")

# 初始化 API 客户端 (从 Streamlit Secrets 读取密钥)
client = OpenAI(api_key=st.secrets["api_key"], base_url="https://api.deepseek.com")

# 侧边栏
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    st.info("专业法律人工智能助手\n\n客服微信：**linwlang12**")
    st.divider()
    st.write("当前版本：v1.0")

# 主界面
st.title("⚖️ 律盾 AI 律师")
st.markdown("---")

tab1, tab2 = st.tabs(["🔍 风险排雷", "✍️ 智能起草"])

with tab1:
    txt = st.text_area("请粘贴需要分析的合同内容或法律条文：", height=250, key="t1")
    if st.button("开始 AI 分析") and txt:
        with st.spinner("AI 律师审阅中..."):
            try:
                r = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role":"user","content":"请作为专业律师分析以下内容的法律风险并给出建议："+txt}]
                )
                st.markdown(r.choices[0].message.content)
            except Exception as e:
                st.error(f"分析出错，请检查 API 密钥。错误信息：{e}")

with tab2:
    req = st.text_area("输入您的文书起草要求（如：起草一份租房合同）：", key="t2")
    if st.button("立即起草") and req:
        with st.spinner("生成中..."):
            try:
                r = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role":"user","content":"请起草一份专业的法律文书："+req}]
                )
                st.info(r.choices[0].message.content)
            except Exception as e:
                st.error(f"生成出错：{e}")
