import streamlit as st

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="律盾 AI - 专业法律顾问",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= 2. 沉浸式 APP 美化 (隐藏多余英文菜单) =================
st.markdown("""
    <style>
    /* 隐藏 Streamlit 顶部的三条杠菜单和 GitHub 图标 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 调整顶部间距，让内容上移 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* 按钮美化：变成律盾金蓝色调 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1E3A8A;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ================= 3. 侧边栏 (会员中心) =================
with st.sidebar:
    st.title("🛡️ 律盾会员中心")
    st.info("当前状态：测试版 (V1.0)")
    st.divider()
    st.write("👤 用户账号：访客模式")
    st.write("📞 技术支持：linwlang12") # 你的微信号已经放进去了
    st.divider()
    if st.button("联系人工客服"):
        st.success("请添加微信：linwlang12")

# ================= 4. 主界面逻辑 =================
st.title("⚖️ 律盾 AI 法律助手")
st.caption("基于大数据深度学习，为您提供 7x24 小时专业法律咨询服务")

# 创建三个功能选项卡
tab1, tab2, tab3 = st.tabs(["💬 法律咨询", "📝 合同审计", "📄 文书模板"])

# --- 选项卡 1: 法律咨询 ---
with tab1:
    st.subheader("智能法律分析")
    user_question = st.text_area(
        "请描述您遇到的法律问题：", 
        placeholder="例如：入职没签劳动合同，被辞退了怎么索赔？",
        height=150
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 开始分析"):
            if user_question:
                with st.spinner("律盾 AI 正在检索最新法律法规..."):
                    # 这里预留 AI 模型接口
                    st.markdown("### 🔍 律盾法律分析报告")
                    st.write("根据您描述的情况，初步分析如下：")
                    st.warning("1. **法律依据**：根据《中华人民共和国劳动合同法》第十条规定...")
                    st.info("2. **核心建议**：建议您收集考勤记录、工资流水等证据...")
                    st.success("💡 提示：此分析仅供参考，复杂案件建议咨询人工律师。")
            else:
                st.error("请输入问题内容后再点击分析。")
    with col2:
        if st.button("🗑️ 清空内容"):
            st.rerun()

# --- 选项卡 2: 合同审计 ---
with tab2:
    st.subheader("合同风险扫描")
    uploaded_file = st.file_uploader("上传合同文件 (支持 PDF/Word)", type=["pdf", "docx"])
    if st.button("🔎 立即扫描风险"):
        if uploaded_file:
            st.info("正在提取合同条款并对比违约风险...")
            st.write("✅ 条款完整度检查完毕")
            st.error("❗ 发现 2 处潜在风险：违约金比例过高、免责条款不清晰。")
        else:
            st.warning("请先上传需要审计的合同文件。")

# --- 选项卡 3: 文书模板 ---
with tab3:
    st.subheader("法律文书一键生成")
    doc_type = st.selectbox("选择文书类型", ["借款协议", "离婚协议书", "劳动仲裁申请书", "律师函"])
    if st.button("📝 生成草案"):
        st.success(f"已为您生成【{doc_type}】标准模板，请根据实际情况填空。")

# ================= 5. 页脚 =================
st.divider()
st.center = st.markdown("<p style='text-align: center; color: gray;'>© 2026 律盾 AI 版权所有</p>", unsafe_allow_html=True)
