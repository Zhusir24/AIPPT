# AI-PPTX Python 版本

基于原始 TypeScript 项目重构的 Python 版本 AI 自动生成 PPT 系统。

## 功能特性

- 🤖 **AI 智能生成**：使用大语言模型自动生成 PPT 大纲和内容
- 📝 **多种输入方式**：支持主题输入、文件上传、网页链接导入
- 🎨 **模板系统**：提供多种精美 PPT 模板
- 👀 **在线预览**：支持生成的 PPT 在线预览
- 📤 **多格式导出**：支持导出 PPTX、PDF 等格式
- 🌐 **现代化界面**：基于 Streamlit 的美观用户界面

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
├── frontend/               # Streamlit 前端
│   ├── components/         # UI 组件
│   ├── pages/             # 页面
│   └── main.py            # 前端入口
├── templates/             # PPT 模板文件
├── static/               # 静态资源
├── tests/                # 测试文件
├── requirements.txt      # 依赖包
└── README.md            # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

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

### 3. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. 启动前端界面

```bash
cd frontend
streamlit run main.py --server.port 8501
```

### 5. 访问应用

打开浏览器访问：http://localhost:8501

## 使用说明

1. **输入内容**：选择输入方式（主题、文件、链接）
2. **AI 生成**：系统调用 AI 模型生成内容大纲
3. **编辑大纲**：可手动调整生成的大纲结构
4. **选择模板**：从预设模板中选择合适的设计
5. **生成 PPT**：系统自动生成完整的 PPTX 文件
6. **预览导出**：在线预览并导出所需格式

## 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite
- **前端**：Streamlit + Python
- **AI 服务**：OpenAI/DeepSeek API
- **PPT 处理**：python-pptx
- **文档处理**：python-docx + BeautifulSoup

## 开源协议

本项目基于 GPL-3.0 开源协议，继承自原始 TypeScript 项目。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题或建议，请创建 Issue 或联系项目维护者。
