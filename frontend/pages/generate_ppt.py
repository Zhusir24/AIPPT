"""
生成PPT页面
"""

import streamlit as st
import requests
import time
import os


def render_generate_page():
    """渲染生成PPT页面"""
    st.markdown('<div class="step-header">⚡ 第四步：生成PPT</div>', unsafe_allow_html=True)
    
    # 检查前置条件
    if not validate_prerequisites():
        return
    
    # 显示项目摘要
    render_project_summary()
    
    st.markdown("---")
    
    # 检查是否已生成PPT
    if st.session_state.project_data.get('generated_file'):
        render_generated_ppt()
    else:
        render_generate_ppt()


def validate_prerequisites():
    """验证前置条件"""
    project_data = st.session_state.project_data
    
    if not project_data.get('outline_content'):
        st.warning("⚠️ 请先生成大纲内容")
        if st.button("⬅️ 返回生成大纲", key="btn_back_to_outline", type="primary"):
            st.session_state.current_step = 2
            st.rerun()
        return False
    
    if not project_data.get('template_id'):
        st.warning("⚠️ 请先选择模板")
        if st.button("⬅️ 返回选择模板", key="btn_back_to_template", type="primary"):
            st.session_state.current_step = 3
            st.rerun()
        return False
    
    return True


def render_project_summary():
    """渲染项目摘要"""
    with st.expander("📋 项目摘要", expanded=False):
        project_data = st.session_state.project_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**标题：** {project_data.get('title', 'N/A')}")
            st.write(f"**输入类型：** {project_data.get('input_type', 'N/A')}")
            st.write(f"**语言：** {project_data['settings'].get('language', 'zh-CN')}")
            
        with col2:
            st.write(f"**模板ID：** {project_data.get('template_id', 'N/A')}")
            st.write(f"**大纲长度：** {len(project_data.get('outline_content', ''))} 字符")
            st.write(f"**详细程度：** {project_data['settings'].get('outline_length', 'regular')}")


def render_generate_ppt():
    """渲染生成PPT界面"""
    st.markdown("#### 🚀 开始生成PPT")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 AI 将根据您的大纲和选择的模板生成完整的 PowerPoint 演示文稿。生成过程可能需要几分钟时间。")
    
    with col2:
        if st.button("⚡ 生成PPT", key="btn_generate_ppt", type="primary", use_container_width=True):
            generate_ppt_content()


def render_generated_ppt():
    """渲染已生成PPT的界面"""
    st.markdown("#### ✅ PPT 已生成完成！")
    
    generated_file = st.session_state.project_data['generated_file']
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.success("🎉 PPT 生成完成！您可以下载文件或重新生成。")
    
    with col2:
        if st.button("🔄 重新生成", key="btn_regenerate_ppt", type="secondary", use_container_width=True):
            st.session_state.project_data['generated_file'] = None
            st.rerun()
    
    # 文件信息
    st.markdown("#### 📄 生成的文件")
    
    file_info_col, download_col = st.columns([2, 1])
    
    with file_info_col:
        st.markdown(f"""
        **文件名：** {os.path.basename(generated_file.get('file_path', 'unknown.pptx'))}  
        **文件大小：** {format_file_size(generated_file.get('file_size', 0))}  
        **生成时间：** {generated_file.get('created_at', 'Unknown')}  
        **幻灯片数量：** {generated_file.get('slide_count', 'Unknown')} 页
        """)
    
    with download_col:
        if generated_file.get('file_path'):
            # 这里需要实现文件下载功能
            if st.button("📥 下载PPT", key="btn_download_ppt", type="primary", use_container_width=True):
                download_ppt_file(generated_file)
    
    # PPT预览（如果有预览图）
    if generated_file.get('preview_images'):
        st.markdown("#### 👁️ PPT 预览")
        render_ppt_preview(generated_file['preview_images'])
    
    st.markdown("---")
    
    # 操作按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 上一步", key="btn_prev_step", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    
    with col2:
        if st.button("🔄 重新开始", key="btn_restart", use_container_width=True, type="secondary"):
            reset_project()
    
    with col3:
        if st.button("✅ 完成", key="btn_complete", use_container_width=True, type="primary"):
            st.balloons()
            st.success("🎉 恭喜！您的PPT演示文稿已成功生成！")


def generate_ppt_content():
    """生成PPT内容"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 第一步：生成详细内容
        status_text.text("🧠 正在生成详细内容...")
        progress_bar.progress(20)
        
        detailed_content = generate_detailed_content()
        if not detailed_content:
            st.error("❌ 详细内容生成失败")
            return
        
        # 第二步：生成PPT文件
        status_text.text("📝 正在生成PPT文件...")
        progress_bar.progress(60)
        
        ppt_result = generate_ppt_file(detailed_content)
        if not ppt_result.get('success'):
            st.error(f"❌ PPT文件生成失败：{ppt_result.get('message')}")
            return
        
        # 第三步：生成预览图
        status_text.text("🖼️ 正在生成预览图...")
        progress_bar.progress(80)
        
        preview_images = generate_preview_images(ppt_result.get('file_path'))
        
        # 完成
        progress_bar.progress(100)
        status_text.text("✅ 生成完成！")
        
        # 保存生成结果
        st.session_state.project_data['generated_file'] = {
            'file_path': ppt_result.get('file_path'),
            'filename': ppt_result.get('filename'),
            'file_size': ppt_result.get('file_size'),
            'created_at': ppt_result.get('created_at', time.strftime('%Y-%m-%d %H:%M:%S')),
            'slide_count': ppt_result.get('slide_count'),
            'download_url': ppt_result.get('download_url'),
            'preview_images': preview_images
        }
        
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 生成过程中发生错误：{str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()


def generate_detailed_content():
    """生成详细内容"""
    try:
        backend_url = st.session_state.api_config['backend_url']
        project_data = st.session_state.project_data
        
        # 准备请求数据
        request_data = {
            "outline": project_data['outline_content'],
            "template_id": project_data['template_id']
        }
        
        # 调用PPT生成API
        response = requests.post(
            f"{backend_url}/api/v1/ai/generate-content",
            json=request_data,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # 获取详细的错误信息
            try:
                error_detail = response.json().get('detail', f'HTTP {response.status_code}')
            except:
                error_detail = f'HTTP {response.status_code}'
            st.error(f"❌ 详细内容生成失败\nAPI错误：{response.status_code}\n错误详情：{error_detail}")
            return None
            
    except Exception as e:
        st.error(f"❌ 生成详细内容失败：{str(e)}")
        return None


def generate_ppt_file(content_data):
    """生成PPT文件"""
    try:
        backend_url = st.session_state.api_config['backend_url']
        project_data = st.session_state.project_data
        
        # 准备请求数据
        request_data = {
            "outline": project_data['outline_content'],
            "template_id": project_data['template_id']
        }
        
        # 调用PPT生成API
        response = requests.post(
            f"{backend_url}/api/v1/ai/generate-ppt",
            json=request_data,
            timeout=180  # 3分钟超时
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    'success': True,
                    'file_path': result['data']['file_path'],
                    'filename': result['data']['filename'],
                    'file_size': result['data']['file_size'],
                    'slide_count': result['data']['slide_count'],
                    'download_url': result['data']['download_url'],
                    'message': result['message']
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', '生成失败')
                }
        else:
            # 获取详细的错误信息
            try:
                error_detail = response.json().get('detail', f'HTTP {response.status_code}')
            except:
                error_detail = f'HTTP {response.status_code}'
            return {
                'success': False,
                'message': f"API错误：{response.status_code} - {error_detail}"
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': "请求超时，PPT生成可能需要更长时间"
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


def generate_preview_images(file_path):
    """生成预览图"""
    # 这里需要实现PPT转图片的功能
    # 暂时返回空列表
    return []


def render_ppt_preview(preview_images):
    """渲染PPT预览"""
    if not preview_images:
        st.info("📷 预览图生成中，请稍后刷新页面")
        return
    
    # 显示预览图网格
    cols_per_row = 3
    for i in range(0, len(preview_images), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(preview_images):
                with cols[j]:
                    st.image(preview_images[i + j], caption=f"第 {i + j + 1} 页", use_column_width=True)


def download_ppt_file(file_info):
    """下载PPT文件"""
    try:
        backend_url = st.session_state.api_config['backend_url']
        
        # 获取下载URL
        if 'download_url' in file_info:
            download_url = f"{backend_url}{file_info['download_url']}"
        else:
            filename = file_info.get('filename', os.path.basename(file_info.get('file_path', '')))
            download_url = f"{backend_url}/api/v1/files/download/{filename}"
        
        # 下载文件
        response = requests.get(download_url, timeout=30)
        if response.status_code == 200:
            # 使用Streamlit的下载按钮
            st.download_button(
                label="📥 点击下载PPT",
                data=response.content,
                file_name=file_info.get('filename', 'presentation.pptx'),
                mime='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                key="download_ppt_btn",
                use_container_width=True
            )
        else:
            st.error(f"❌ 下载失败：{response.status_code}")
            
    except Exception as e:
        st.error(f"❌ 下载失败：{str(e)}")


def reset_project():
    """重置项目"""
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
            'target_audience': '一般受众',
            'presentation_duration': '15-20分钟',
            'more_requirements': ''
        }
    }
    st.rerun()


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_file_size(file_path):
    """获取文件大小"""
    try:
        if isinstance(file_path, str) and os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except:
        return 0 