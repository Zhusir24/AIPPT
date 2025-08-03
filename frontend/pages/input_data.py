"""
输入数据页面
"""

import streamlit as st
import requests


def render_input_page():
    """渲染输入数据页面"""
    st.markdown('<div class="step-header">📝 第一步：输入内容</div>', unsafe_allow_html=True)
    
    with st.container():
        # 输入方式选择
        st.markdown("#### 选择输入方式")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💭 输入主题", use_container_width=True, type="primary" if st.session_state.project_data['input_type'] == 'topic' else "secondary"):
                st.session_state.project_data['input_type'] = 'topic'
        
        with col2:
            if st.button("📄 上传文件", use_container_width=True, type="primary" if st.session_state.project_data['input_type'] == 'file' else "secondary"):
                st.session_state.project_data['input_type'] = 'file'
        
        with col3:
            if st.button("🔗 网页链接", use_container_width=True, type="primary" if st.session_state.project_data['input_type'] == 'url' else "secondary"):
                st.session_state.project_data['input_type'] = 'url'
        
        st.markdown("---")
        
        # 根据选择的输入方式显示对应界面
        input_type = st.session_state.project_data['input_type']
        
        if input_type == 'topic':
            render_topic_input()
        elif input_type == 'file':
            render_file_input()
        elif input_type == 'url':
            render_url_input()
        
        st.markdown("---")
        
        # 高级设置
        render_advanced_settings()
        
        st.markdown("---")
        
        # 下一步按钮
        if st.button("🚀 下一步：生成大纲", use_container_width=True, type="primary"):
            if validate_input():
                st.session_state.current_step = 2
                st.rerun()


def render_topic_input():
    """渲染主题输入界面"""
    st.markdown("#### 💭 输入演示主题和要求")
    
    # 项目标题
    title = st.text_input(
        "演示文稿标题",
        value=st.session_state.project_data.get('title', ''),
        placeholder="例如：2025年就业市场预测"
    )
    st.session_state.project_data['title'] = title
    
    # 主要内容
    content = st.text_area(
        "主题内容和具体要求",
        value=st.session_state.project_data.get('input_content', ''),
        placeholder="""请详细描述您的演示主题，包括：
- 主要议题和目标
- 目标听众
- 希望涵盖的要点
- 特殊要求或注意事项

例如：分析2025年就业市场趋势，包括新兴行业、技能需求变化、薪资水平预测，面向应届毕业生和求职者。""",
        height=200
    )
    st.session_state.project_data['input_content'] = content
    
    # 快速示例
    st.markdown("#### 💡 快速示例")
    examples = [
        "人工智能在医疗领域的应用",
        "可持续发展的商业策略",
        "远程工作的未来趋势",
        "区块链技术入门指南"
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"📝 {example}", key=f"example_{i}"):
                st.session_state.project_data['title'] = example
                st.session_state.project_data['input_content'] = f"请创建关于\"{example}\"的详细演示文稿，包括概念介绍、应用场景、发展趋势和实际案例。"
                st.rerun()


def render_file_input():
    """渲染文件上传界面"""
    st.markdown("#### 📄 上传文档文件")
    
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['pdf', 'docx', 'txt', 'md'],
        help="支持 PDF、Word、文本和 Markdown 文件"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"✅ 已上传：{uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # 上传文件到后端并提取内容
        if st.button("📊 提取文件内容", type="primary"):
            with st.spinner("正在处理文件..."):
                try:
                    backend_url = st.session_state.api_config['backend_url']
                    files = {"file": uploaded_file.getvalue()}
                    
                    response = requests.post(
                        f"{backend_url}/api/v1/files/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            content = result.get('extracted_content', '')
                            st.session_state.project_data['input_content'] = content
                            st.session_state.project_data['title'] = uploaded_file.name.split('.')[0]
                            
                            st.success("✅ 文件内容提取成功！")
                            st.text_area("提取的内容预览", value=content[:500] + "..." if len(content) > 500 else content, height=200)
                        else:
                            st.error(f"❌ 文件处理失败：{result.get('message')}")
                    else:
                        st.error("❌ 服务器连接失败")
                        
                except Exception as e:
                    st.error(f"❌ 文件上传失败：{str(e)}")


def render_url_input():
    """渲染URL输入界面"""
    st.markdown("#### 🔗 从网页提取内容")
    
    url = st.text_input(
        "网页地址",
        placeholder="https://example.com/article",
        help="输入包含相关内容的网页URL"
    )
    
    if url and st.button("🌐 提取网页内容", type="primary"):
        with st.spinner("正在提取网页内容..."):
            try:
                backend_url = st.session_state.api_config['backend_url']
                
                response = requests.post(
                    f"{backend_url}/api/v1/files/extract-url",
                    params={"url": url}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        content = result['data']['content']
                        st.session_state.project_data['input_content'] = content
                        st.session_state.project_data['title'] = f"来自 {url} 的内容"
                        
                        st.success("✅ 网页内容提取成功！")
                        st.text_area("提取的内容预览", value=content[:500] + "..." if len(content) > 500 else content, height=200)
                    else:
                        st.error(f"❌ 内容提取失败：{result.get('message')}")
                else:
                    st.error("❌ 服务器连接失败")
                    
            except Exception as e:
                st.error(f"❌ 网页内容提取失败：{str(e)}")


def render_advanced_settings():
    """渲染高级设置"""
    with st.expander("⚙️ 高级设置", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "演示语言",
                options=["中文", "英文", "日文", "韩文"],
                format_func=lambda x: {"中文": "中文 (简体)", "英文": "English", "日文": "日本語", "韩文": "한국어"}[x],
                index=0
            )
            st.session_state.project_data['settings']['language'] = language
        
        with col2:
            outline_length = st.selectbox(
                "大纲详细程度",
                options=["简短", "中等", "详细"],
                format_func=lambda x: {"简短": "简洁版 (3-5个主要章节)", "中等": "标准版 (5-8个主要章节)", "详细": "详细版 (8-12个主要章节)"}[x],
                index=1
            )
            st.session_state.project_data['settings']['outline_length'] = outline_length
        
        more_requirements = st.text_area(
            "补充要求",
            value=st.session_state.project_data['settings'].get('more_requirements', ''),
            placeholder="可以添加特殊要求，如：目标听众、演示时长、特定格式要求等",
            height=100
        )
        st.session_state.project_data['settings']['more_requirements'] = more_requirements


def validate_input():
    """验证输入数据"""
    project_data = st.session_state.project_data
    
    if not project_data.get('input_content'):
        st.error("❌ 请输入内容或上传文件")
        return False
    
    if len(project_data['input_content']) < 10:
        st.error("❌ 输入内容太短，请提供更详细的信息")
        return False
    
    if not project_data.get('title'):
        st.warning("⚠️ 建议设置一个演示标题")
        project_data['title'] = "AI 生成的演示文稿"
    
    return True 