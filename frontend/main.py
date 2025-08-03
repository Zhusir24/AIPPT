"""
AI-PPTX 前端主入口文件
基于 Streamlit 构建的用户界面
"""

import streamlit as st
import requests
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from components.sidebar import render_sidebar
from pages.input_data import render_input_page
from pages.generate_outline import render_outline_page
from pages.select_template import render_template_page
from pages.generate_ppt import render_generate_page
from pages.settings import render_settings_page

# 配置页面
st.set_page_config(
    page_title="AI-PPTX",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 隐藏Streamlit默认菜单 */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {display: none;}
    
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .step-header {
        color: #667eea;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化会话状态"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    if 'project_data' not in st.session_state:
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
    
    if 'api_config' not in st.session_state:
        st.session_state.api_config = {
            'backend_url': 'http://localhost:8000',
            'ai_provider': 'openai',
            'api_key': ''
        }

def render_header():
    """渲染页面头部"""
    st.markdown("""
        <div class="main-header">
            <h1>🤖 AI-PPTX 演示文稿生成器</h1>
            <p>使用人工智能技术，一键生成专业的 PowerPoint 演示文稿</p>
        </div>
    """, unsafe_allow_html=True)

def render_progress_bar():
    """渲染进度条"""
    step_names = ["输入内容", "生成大纲", "选择模板", "生成PPT", "完成"]
    current_step = st.session_state.current_step
    
    cols = st.columns(5)
    for i, (col, step_name) in enumerate(zip(cols, step_names), 1):
        with col:
            if i < current_step:
                st.markdown(f"✅ **{step_name}**")
            elif i == current_step:
                st.markdown(f"🔄 **{step_name}**")
            else:
                st.markdown(f"⏳ {step_name}")

def main():
    """主函数"""
    initialize_session_state()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染头部
    render_header()
    
    # 渲染进度条
    render_progress_bar()
    
    st.markdown("---")
    
    # 根据当前步骤渲染对应页面
    current_step = st.session_state.current_step
    
    if current_step == 1:
        render_input_page()
    elif current_step == 2:
        render_outline_page()
    elif current_step == 3:
        render_template_page()
    elif current_step == 4:
        render_generate_page()
    elif current_step == 0:  # 设置页面
        render_settings_page()
    
    # 页面底部信息
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>🚀 基于 FastAPI + Streamlit 构建 | 💡 支持 OpenAI、DeepSeek 等多种 AI 模型</p>
            <p>📧 如有问题请联系技术支持 | 🔗 <a href="http://localhost:8000/docs" target="_blank">查看 API 文档</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 