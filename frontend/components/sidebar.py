"""
侧边栏组件
"""

import streamlit as st
import requests


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("### 🎯 操作导航")
        
        # 步骤导航
        if st.button("📝 输入内容", use_container_width=True):
            st.session_state.current_step = 1
        
        if st.button("🧠 生成大纲", use_container_width=True):
            st.session_state.current_step = 2
        
        if st.button("🎨 选择模板", use_container_width=True):
            st.session_state.current_step = 3
        
        if st.button("⚡ 生成PPT", use_container_width=True):
            st.session_state.current_step = 4
        
        st.markdown("---")
        
        # 其他功能
        if st.button("⚙️ 系统设置", use_container_width=True):
            st.session_state.current_step = 0
        
        if st.button("🔄 重新开始", use_container_width=True):
            # 重置所有数据
            st.session_state.current_step = 1
            st.session_state.project_data = {
                'title': '',
                'input_type': 'topic',
                'input_content': '',
                'outline_content': '',
                'template_id': None,
                'generated_file': None,
                'settings': {
                    'language': '中文',
                    'outline_length': '中等',
                    'more_requirements': ''
                }
            }
            st.rerun()
        
        st.markdown("---")
        
        # 项目信息
        st.markdown("### 📊 项目状态")
        project_data = st.session_state.project_data
        
        if project_data.get('title'):
            st.markdown(f"**标题：** {project_data['title'][:20]}...")
        
        if project_data.get('input_content'):
            st.markdown(f"**输入长度：** {len(project_data['input_content'])} 字符")
        
        if project_data.get('outline_content'):
            st.markdown("✅ 大纲已生成")
        
        if project_data.get('template_id'):
            st.markdown(f"✅ 模板已选择 (ID: {project_data['template_id']})")
        
        if project_data.get('generated_file'):
            st.markdown("✅ PPT 已生成")
        
        st.markdown("---")
        
        # 快捷信息
        st.markdown("### 💡 使用提示")
        st.markdown("""
        1. **输入内容**：可以输入主题、上传文件或提供网页链接
        2. **生成大纲**：AI 会根据输入生成结构化大纲
        3. **选择模板**：从多种专业模板中选择合适的设计
        4. **生成PPT**：自动生成完整的演示文稿
        """)
        
        # 技术信息
        st.markdown("### 🔧 技术信息")
        
        # 获取AI提供商信息
        try:
            backend_url = st.session_state.api_config.get('backend_url', 'N/A')
            response = requests.get(f"{backend_url}/api/v1/ai/provider", timeout=5)
            if response.status_code == 200:
                provider_info = response.json().get('data', {})
                ai_provider = provider_info.get('provider', 'N/A')
                model_name = provider_info.get('model', 'N/A')
            else:
                ai_provider = "DeepSeek"  # 默认显示
                model_name = "deepseek-chat"
        except:
            ai_provider = "DeepSeek"  # 默认显示
            model_name = "deepseek-chat"
        
        st.markdown(f"""
        - **后端服务**：{backend_url}
        - **AI 提供商**：{ai_provider}
        - **模型**：{model_name}
        - **当前步骤**：{st.session_state.current_step}/4
        """)
        
        # 版本信息
        st.markdown("---")
        st.markdown("**AI-PPTX v1.0**")
        st.markdown("*Python 版本*") 