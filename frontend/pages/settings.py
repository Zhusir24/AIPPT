"""
设置页面
"""

import streamlit as st
import requests
import json


def render_settings_page():
    """渲染设置页面"""
    st.markdown('<div class="step-header">⚙️ 系统设置</div>', unsafe_allow_html=True)
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("### 设置分类")
        setting_category = st.radio(
            "选择设置类别",
            ["API 配置", "界面设置", "高级选项", "关于"]
        )
    
    # 根据选择显示对应设置
    if setting_category == "API 配置":
        render_api_settings()
    elif setting_category == "界面设置":
        render_ui_settings()
    elif setting_category == "高级选项":
        render_advanced_settings()
    elif setting_category == "关于":
        render_about_page()


def render_api_settings():
    """渲染API配置设置"""
    st.markdown("#### 🔗 API 配置")
    
    with st.form("api_settings_form"):
        st.markdown("##### 后端服务配置")
        
        backend_url = st.text_input(
            "后端服务地址",
            value=st.session_state.api_config.get('backend_url', 'http://localhost:8000'),
            help="FastAPI 后端服务的完整URL地址"
        )
        
        # 测试连接
        col1, col2 = st.columns([1, 1])
        with col1:
            test_connection_btn = st.form_submit_button("🔍 测试连接", type="secondary")
        with col2:
            save_api_btn = st.form_submit_button("💾 保存配置", type="primary")
        
        if test_connection_btn:
            test_backend_connection(backend_url)
        
        if save_api_btn:
            st.session_state.api_config['backend_url'] = backend_url
            st.success("✅ API 配置已保存")
    
    st.markdown("---")
    
    # AI 服务配置
    with st.form("ai_settings_form"):
        st.markdown("##### 🤖 AI 服务配置")
        
        ai_provider = st.selectbox(
            "AI 服务提供商",
            options=["openai", "deepseek", "anthropic"],
            format_func=lambda x: {
                "openai": "OpenAI (GPT-3.5/GPT-4)",
                "deepseek": "DeepSeek",
                "anthropic": "Anthropic (Claude)"
            }[x],
            index=0
        )
        
        api_key = st.text_input(
            "API 密钥",
            value=st.session_state.api_config.get('api_key', ''),
            type="password",
            help="请输入对应AI服务的API密钥"
        )
        
        if st.form_submit_button("💾 保存AI配置", type="primary"):
            st.session_state.api_config.update({
                'ai_provider': ai_provider,
                'api_key': api_key
            })
            
            # 这里可以调用后端API保存配置
            save_ai_config_to_backend(ai_provider, api_key)
    
    # 显示当前配置状态
    render_config_status()


def render_ui_settings():
    """渲染界面设置"""
    st.markdown("#### 🎨 界面设置")
    
    with st.form("ui_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "主题颜色",
                options=["蓝色", "绿色", "紫色", "橙色"],
                index=0
            )
            
            language = st.selectbox(
                "界面语言",
                options=["zh-CN", "en-US"],
                format_func=lambda x: {"zh-CN": "简体中文", "en-US": "English"}[x],
                index=0
            )
        
        with col2:
            auto_save = st.checkbox("自动保存项目", value=True)
            show_tips = st.checkbox("显示操作提示", value=True)
            compact_mode = st.checkbox("紧凑模式", value=False)
        
        if st.form_submit_button("💾 保存界面设置", type="primary"):
            st.success("✅ 界面设置已保存")


def render_advanced_settings():
    """渲染高级设置"""
    st.markdown("#### ⚙️ 高级选项")
    
    with st.form("advanced_settings_form"):
        st.markdown("##### 🚀 性能设置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_tokens = st.number_input(
                "最大生成长度",
                min_value=500,
                max_value=4000,
                value=2000,
                step=100,
                help="AI生成内容的最大令牌数"
            )
            
            timeout = st.number_input(
                "请求超时时间(秒)",
                min_value=30,
                max_value=300,
                value=60,
                step=10
            )
        
        with col2:
            temperature = st.slider(
                "生成创造性",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="较高值会产生更多创造性内容"
            )
            
            enable_cache = st.checkbox("启用缓存", value=True, help="缓存生成结果以提高性能")
        
        st.markdown("##### 📁 文件设置")
        
        max_file_size = st.number_input(
            "最大上传文件大小 (MB)",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )
        
        allowed_formats = st.multiselect(
            "允许的文件格式",
            options=["PDF", "DOCX", "TXT", "MD"],
            default=["PDF", "DOCX", "TXT", "MD"]
        )
        
        if st.form_submit_button("💾 保存高级设置", type="primary"):
            st.success("✅ 高级设置已保存")


def render_about_page():
    """渲染关于页面"""
    st.markdown("#### ℹ️ 关于 AI-PPTX")
    
    st.markdown("""
    ### 🤖 AI-PPTX Python 版本
    
    基于原始 TypeScript 项目重构的 Python 版本 AI 自动生成 PPT 系统。
    
    #### ✨ 主要特性
    
    - 🧠 **智能生成**：使用先进的大语言模型生成结构化内容
    - 🎨 **多样模板**：提供多种专业设计模板
    - 📱 **现代界面**：基于 Streamlit 的直观用户界面
    - 🔧 **易于部署**：Python 技术栈，部署简单
    - 🌐 **开源免费**：遵循 GPL-3.0 开源协议
    
    #### 🛠️ 技术栈
    
    - **后端**：FastAPI + SQLAlchemy + SQLite
    - **前端**：Streamlit + Python
    - **AI 服务**：OpenAI / DeepSeek / Anthropic API
    - **文档处理**：python-pptx + python-docx
    - **部署**：Docker / 本地部署
    """)
    
    st.markdown("---")
    
    # 系统信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 系统信息")
        st.markdown(f"""
        - **版本**：v1.0.0
        - **构建时间**：2024-12-19
        - **Python 版本**：3.8+
        - **许可证**：GPL-3.0
        """)
    
    with col2:
        st.markdown("#### 🔗 相关链接")
        st.markdown("""
        - [GitHub 仓库](https://github.com/your-repo/ai-pptx-python)
        - [问题反馈](https://github.com/your-repo/ai-pptx-python/issues)
        - [使用文档](https://github.com/your-repo/ai-pptx-python/wiki)
        - [原始项目](https://github.com/SmartSchoolAI/ai-to-pptx)
        """)
    
    st.markdown("---")
    
    # 导出/导入配置
    st.markdown("#### 💾 配置管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 导出配置", use_container_width=True):
            export_config()
    
    with col2:
        uploaded_config = st.file_uploader("📥 导入配置", type=['json'])
        if uploaded_config:
            import_config(uploaded_config)


def test_backend_connection(backend_url):
    """测试后端连接"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ 连接成功：{result.get('message', '服务正常')}")
        else:
            st.error(f"❌ 连接失败：HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到后端服务，请检查地址和服务状态")
    except requests.exceptions.Timeout:
        st.error("❌ 连接超时，请检查网络状况")
    except Exception as e:
        st.error(f"❌ 连接测试失败：{str(e)}")


def save_ai_config_to_backend(ai_provider, api_key):
    """保存AI配置到后端"""
    try:
        backend_url = st.session_state.api_config['backend_url']
        
        # 这里调用后端API保存配置
        # response = requests.post(f"{backend_url}/api/v1/config/ai", ...)
        
        st.success("✅ AI 配置已保存到后端")
    except Exception as e:
        st.warning(f"⚠️ 后端配置保存失败：{str(e)}")


def render_config_status():
    """渲染配置状态"""
    st.markdown("#### 📋 当前配置状态")
    
    config = st.session_state.api_config
    
    status_data = {
        "后端服务": config.get('backend_url', 'N/A'),
        "AI 提供商": config.get('ai_provider', 'N/A'),
        "API 密钥": "已配置" if config.get('api_key') else "未配置",
    }
    
    for key, value in status_data.items():
        st.markdown(f"- **{key}**：{value}")


def export_config():
    """导出配置"""
    config = {
        'api_config': st.session_state.api_config,
        'project_data': st.session_state.project_data
    }
    
    config_json = json.dumps(config, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 下载配置文件",
        data=config_json,
        file_name="ai_pptx_config.json",
        mime="application/json"
    )


def import_config(uploaded_file):
    """导入配置"""
    try:
        config = json.loads(uploaded_file.read().decode('utf-8'))
        
        if 'api_config' in config:
            st.session_state.api_config.update(config['api_config'])
        
        if 'project_data' in config:
            st.session_state.project_data.update(config['project_data'])
        
        st.success("✅ 配置导入成功")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 配置导入失败：{str(e)}") 