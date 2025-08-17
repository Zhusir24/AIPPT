# AI-PPTX Python 版本

基于原始 TypeScript 项目重构的 Python 版本 AI 自动生成 PPT 系统。

## 功能特性

- 🤖 **AI 智能生成**：使用大语言模型自动生成 PPT 大纲和内容
- 📝 **多种输入方式**：支持主题输入、文件上传、网页链接导入
- 🎨 **模板系统**：提供多种精美 PPT 模板
- 👀 **在线预览**：支持生成的 PPT 在线预览
- 📤 **多格式导出**：支持导出 PPTX、PDF 等格式
- 🌐 **现代化界面**：基于 HTML5 的响应式美观用户界面

## 项目结构

```
ai-pptx-python/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务服务
│   │   └── utils/          # 工具函数
│   └── main.py             # 后端入口
├── frontend_html/          # HTML 前端
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript 文件
│   └── index.html         # 主页面
├── templates/             # PPT 模板文件
├── static/               # 静态资源
├── tests/                # 测试文件
├── start.py              # 一键启动脚本
├── requirements.txt      # 依赖包
└── README.md            # 项目说明
```

## 快速开始

### 方式一：一键启动（推荐）

```bash
# 自动安装依赖、启动前后端服务、打开浏览器
python3 start.py
```

这将自动完成：
- ✅ 检查和安装依赖包
- 🚀 启动后端服务（http://localhost:8000）
- 🎨 启动HTML前端（http://localhost:8080）
- 🌐 自动打开浏览器

### 方式二：手动启动

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

创建 `.env` 文件：

```env
# AI API 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# DeepSeek API 配置（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 应用配置
APP_NAME=AI-PPTX
DEBUG=True
```

#### 3. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### 4. 启动HTML前端

```bash
# 方式1：使用脚本
./run_html_frontend.sh

# 方式2：使用Python
python3 run_frontend_html.py
```

#### 5. 访问应用

打开浏览器访问：http://localhost:8080

## 使用说明

1. **输入内容**：选择输入方式（主题、文件、链接）
2. **AI 生成**：系统调用 AI 模型生成内容大纲
3. **编辑大纲**：可手动调整生成的大纲结构
4. **选择模板**：从预设模板中选择合适的设计
5. **生成 PPT**：系统自动生成完整的 PPTX 文件
6. **预览导出**：在线预览并导出所需格式

## 界面特色

### 🎨 现代化HTML前端
- ✨ **美观设计**：渐变背景、流畅动画、响应式布局
- 🚀 **快速响应**：纯前端技术，无Python运行时依赖
- 📱 **跨设备适配**：完美支持桌面、平板、手机访问
- 🎯 **用户体验**：直观的进度指示器和交互反馈

### 🛠️ 功能亮点
- 📊 **动态进度条**：实时显示生成进度，步骤可视化
- 🔄 **智能状态管理**：自动保存用户输入和操作状态
- 📁 **拖拽上传**：支持文件拖拽上传，操作更便捷
- ⚙️ **设置管理**：可配置API服务、界面主题等选项
- 🌐 **浏览器兼容**：支持Chrome、Firefox、Safari、Edge等主流浏览器

## 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite
- **前端**：HTML5 + CSS3 + JavaScript ES6+
- **AI 服务**：OpenAI/DeepSeek API
- **PPT 处理**：python-pptx
- **文档处理**：python-docx + BeautifulSoup
- **服务部署**：Python HTTP Server

## 开源协议

本项目基于 GPL-3.0 开源协议，继承自原始 TypeScript 项目。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题或建议，请创建 Issue 或联系项目维护者。
