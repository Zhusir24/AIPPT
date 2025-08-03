"""
选择模板页面
"""

import streamlit as st
import requests


def render_template_page():
    """渲染选择模板页面"""
    st.markdown('<div class="step-header">🎨 第三步：选择模板</div>', unsafe_allow_html=True)
    
    # 检查是否有大纲内容
    if not st.session_state.project_data.get('outline_content'):
        st.warning("⚠️ 请先生成大纲内容")
        if st.button("⬅️ 返回生成大纲", type="primary"):
            st.session_state.current_step = 2
            st.rerun()
        return
    
    # 加载模板列表
    load_templates()


def load_templates():
    """加载模板列表"""
    if 'templates' not in st.session_state:
        with st.spinner("🎨 正在加载模板..."):
            try:
                backend_url = st.session_state.api_config['backend_url']
                response = requests.get(f"{backend_url}/api/v1/templates/")
                
                if response.status_code == 200:
                    st.session_state.templates = response.json()
                else:
                    st.error("❌ 无法加载模板列表")
                    st.session_state.templates = []
            except Exception as e:
                st.error(f"❌ 加载模板失败：{str(e)}")
                st.session_state.templates = get_default_templates()
    
    render_template_selection()


def render_template_selection():
    """渲染模板选择界面"""
    templates = st.session_state.get('templates', [])
    
    if not templates:
        st.warning("⚠️ 暂无可用模板")
        render_navigation_buttons()
        return
    
    st.markdown("#### 🎯 选择演示模板")
    st.info("💡 选择一个适合您演示主题的模板设计。模板将决定 PPT 的整体风格和布局。")
    
    # 模板分类筛选
    categories = list(set([t.get('category', '默认') for t in templates if t.get('category')]))
    if categories:
        selected_category = st.selectbox(
            "🗂️ 模板分类",
            options=['全部'] + categories,
            index=0
        )
        
        if selected_category != '全部':
            templates = [t for t in templates if t.get('category') == selected_category]
    
    # 模板网格显示
    render_template_grid(templates)
    
    st.markdown("---")
    render_navigation_buttons()


def render_template_grid(templates):
    """渲染模板网格"""
    # 每行显示3个模板
    cols_per_row = 3
    rows = (len(templates) + cols_per_row - 1) // cols_per_row
    
    current_template_id = st.session_state.project_data.get('template_id')
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            template_idx = row * cols_per_row + col_idx
            if template_idx >= len(templates):
                break
                
            template = templates[template_idx]
            with cols[col_idx]:
                render_template_card(template, current_template_id)


def render_template_card(template, current_template_id):
    """渲染单个模板卡片"""
    template_id = template.get('id')
    is_selected = template_id == current_template_id
    
    # 模板卡片容器
    card_style = """
        border: 2px solid {};
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: {};
    """.format(
        "#667eea" if is_selected else "#ddd",
        "#f0f8ff" if is_selected else "white"
    )
    
    with st.container():
        st.markdown(f'<div style="{card_style}">', unsafe_allow_html=True)
        
        # 模板预览图
        preview_image = template.get('preview_image')
        if preview_image:
            # 构建完整的图片URL
            backend_url = st.session_state.api_config['backend_url']
            if preview_image.startswith('templates/'):
                image_url = f"{backend_url}/{preview_image}"
            else:
                image_url = preview_image
            st.image(image_url, use_column_width=True)
        else:
            # 默认预览图
            st.markdown("""
                <div style="
                    height: 150px; 
                    background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 5px;
                    margin-bottom: 10px;
                ">
                    <span style="color: #666; font-size: 48px;">🎨</span>
                </div>
            """, unsafe_allow_html=True)
        
        # 模板信息
        st.markdown(f"**{template.get('name', '未命名模板')}**")
        
        description = template.get('description', '暂无描述')
        if len(description) > 50:
            description = description[:50] + "..."
        st.markdown(f"<small>{description}</small>", unsafe_allow_html=True)
        
        # 模板标签
        category = template.get('category')
        if category:
            st.markdown(f"<span style='background: #e1f5fe; padding: 2px 8px; border-radius: 12px; font-size: 12px;'>{category}</span>", unsafe_allow_html=True)
        
        # 选择按钮
        button_text = "✅ 已选择" if is_selected else "选择此模板"
        button_type = "secondary" if is_selected else "primary"
        
        if st.button(button_text, key=f"template_{template_id}", type=button_type, use_container_width=True):
            if not is_selected:
                st.session_state.project_data['template_id'] = template_id
                st.success(f"✅ 已选择模板：{template.get('name')}")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_navigation_buttons():
    """渲染导航按钮"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 上一步", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("🔄 刷新模板", use_container_width=True, type="secondary"):
            if 'templates' in st.session_state:
                del st.session_state.templates
            st.rerun()
    
    with col3:
        template_id = st.session_state.project_data.get('template_id')
        if template_id:
            if st.button("➡️ 下一步：生成PPT", use_container_width=True, type="primary"):
                st.session_state.current_step = 4
                st.rerun()
        else:
            st.button("➡️ 请先选择模板", use_container_width=True, disabled=True)


def get_default_templates():
    """获取默认模板列表（当服务器不可用时）"""
    return [
        {
            "id": 1,
            "name": "商务蓝",
            "description": "专业的商务风格，适合企业演示和工作汇报",
            "category": "商务",
            "preview_image": None
        },
        {
            "id": 2,
            "name": "简约白",
            "description": "简洁清爽的设计，适合学术演示和技术分享",
            "category": "简约",
            "preview_image": None
        },
        {
            "id": 3,
            "name": "活力橙",
            "description": "充满活力的色彩搭配，适合创意展示和产品发布",
            "category": "创意",
            "preview_image": None
        },
        {
            "id": 4,
            "name": "科技紫",
            "description": "现代科技感设计，适合技术演示和创新项目",
            "category": "科技",
            "preview_image": None
        }
    ] 