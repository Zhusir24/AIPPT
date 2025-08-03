"""
生成大纲页面
"""

import streamlit as st
import requests
import json
import time


def render_outline_page():
    """渲染生成大纲页面"""
    st.markdown('<div class="step-header">🧠 第二步：生成大纲</div>', unsafe_allow_html=True)
    
    # 显示输入内容摘要
    with st.expander("📋 输入内容摘要", expanded=False):
        project_data = st.session_state.project_data
        st.write(f"**标题：** {project_data.get('title', 'N/A')}")
        st.write(f"**输入类型：** {project_data.get('input_type', 'N/A')}")
        st.write(f"**语言：** {project_data['settings'].get('language', 'zh-CN')}")
        st.write(f"**详细程度：** {project_data['settings'].get('outline_length', 'regular')}")
        
        content = project_data.get('input_content', '')
        if content:
            st.text_area("输入内容", value=content[:300] + "..." if len(content) > 300 else content, height=100, disabled=True)
    
    st.markdown("---")
    
    # 检查是否已有大纲
    if st.session_state.project_data.get('outline_content'):
        render_existing_outline()
    else:
        render_generate_outline()


def render_generate_outline():
    """渲染生成大纲界面"""
    st.markdown("#### 🚀 开始生成大纲")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 AI 将根据您的输入内容自动生成结构化的演示大纲，包括主要章节和要点。")
    
    with col2:
        generate_btn = st.button("🧠 生成大纲", type="primary", use_container_width=True)
    
    if generate_btn:
        generate_outline_content()


def render_existing_outline():
    """渲染已有大纲的编辑界面"""
    st.markdown("#### ✅ 大纲已生成")
    
    # 显示生成的大纲
    outline_content = st.session_state.project_data['outline_content']
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.success("🎉 大纲生成完成！您可以直接使用或进行修改。")
    
    with col2:
        if st.button("🔄 重新生成", type="secondary", use_container_width=True):
            st.session_state.project_data['outline_content'] = ''
            st.rerun()
    
    # 可编辑的大纲内容
    st.markdown("#### 📝 编辑大纲内容")
    edited_outline = st.text_area(
        "大纲内容（Markdown 格式）",
        value=outline_content,
        height=400,
        help="您可以修改大纲的结构和内容。支持 Markdown 格式。"
    )
    
    # 更新大纲内容
    if edited_outline != outline_content:
        st.session_state.project_data['outline_content'] = edited_outline
    
    # 大纲预览
    with st.expander("👁️ 大纲预览", expanded=True):
        st.markdown(edited_outline)
    
    st.markdown("---")
    
    # 导航按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 上一步", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("💾 保存大纲", use_container_width=True, type="secondary"):
            st.success("💾 大纲已保存！")
    
    with col3:
        if st.button("➡️ 下一步：选择模板", use_container_width=True, type="primary"):
            st.session_state.current_step = 3
            st.rerun()


def generate_outline_content():
    """生成大纲内容"""
    with st.spinner("🤖 AI 正在生成大纲，请稍候..."):
        try:
            backend_url = st.session_state.api_config['backend_url']
            project_data = st.session_state.project_data
            
            # 准备请求数据 - 使用新的字段结构
            request_data = {
                "topic": project_data['input_content'],  # 使用新字段名
                "language": project_data['settings']['language'],
                "outline_length": project_data['settings']['outline_length'],
                "target_audience": project_data['settings'].get('target_audience', '一般受众'),
                "presentation_duration": project_data['settings'].get('presentation_duration', '15-20分钟'),
                "additional_requirements": project_data['settings'].get('more_requirements', '')
            }
            
            # 调用生成大纲API
            response = requests.post(
                f"{backend_url}/api/v1/ai/generate-outline",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                outline_markdown = result.get('outline_markdown', '')
                
                if outline_markdown:
                    st.session_state.project_data['outline_content'] = outline_markdown
                    st.success("🎉 大纲生成成功！")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 生成的大纲内容为空")
            else:
                error_detail = "服务器错误"
                try:
                    error_response = response.json()
                    error_detail = error_response.get('detail', error_detail)
                except:
                    pass
                st.error(f"❌ 大纲生成失败：{error_detail}")
                
        except requests.exceptions.Timeout:
            st.error("❌ 请求超时，请检查网络连接或稍后重试")
        except requests.exceptions.ConnectionError:
            st.error("❌ 无法连接到后端服务，请确保后端服务正在运行")
        except Exception as e:
            st.error(f"❌ 发生未知错误：{str(e)}")


def generate_outline_stream():
    """流式生成大纲内容（SSE）"""
    backend_url = st.session_state.api_config['backend_url']
    project_data = st.session_state.project_data
    
    # 准备请求数据 - 使用新的字段结构
    request_data = {
        "topic": project_data['input_content'],  # 使用新字段名
        "language": project_data['settings']['language'],
        "outline_length": project_data['settings']['outline_length'],
        "target_audience": project_data['settings'].get('target_audience', '一般受众'),
        "presentation_duration": project_data['settings'].get('presentation_duration', '15-20分钟'),
        "additional_requirements": project_data['settings'].get('more_requirements', '')
    }
    
    # 创建流式显示容器
    status_container = st.empty()
    content_container = st.empty()
    
    try:
        import sseclient  # 需要安装 sseclient-py
        
        response = requests.post(
            f"{backend_url}/api/v1/ai/generate-outline-stream",
            json=request_data,
            stream=True,
            headers={'Accept': 'text/event-stream'}
        )
        
        client = sseclient.SSEClient(response)
        collected_content = ""
        
        for event in client.events():
            if event.data:
                try:
                    data = json.loads(event.data)
                    
                    if data.get('type') == 'content':
                        collected_content = data.get('full_content', '')
                        # 实时更新显示
                        with content_container:
                            st.markdown("#### 🔄 正在生成...")
                            st.markdown(collected_content)
                    
                    elif data.get('type') == 'complete':
                        final_content = data.get('outline_markdown', '')
                        st.session_state.project_data['outline_content'] = final_content
                        status_container.success("🎉 大纲生成完成！")
                        break
                    
                    elif data.get('type') == 'error':
                        status_container.error(f"❌ 生成失败：{data.get('message')}")
                        break
                        
                except json.JSONDecodeError:
                    continue
                    
    except ImportError:
        st.warning("⚠️ 流式生成功能需要安装 sseclient-py，使用标准模式生成")
        generate_outline_content()
    except Exception as e:
        st.error(f"❌ 流式生成失败：{str(e)}")
        # 降级到标准生成模式
        generate_outline_content() 