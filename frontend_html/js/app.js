/**
 * AI-PPTX 前端应用主逻辑
 * 处理用户交互、状态管理、界面更新等
 */

class AIPPTXApp {
    constructor() {
        this.currentStep = 1;
        this.projectData = {
            title: '',
            inputType: 'topic',
            inputContent: '',
            outlineContent: '',
            templateId: null,
            generatedFile: null,
            settings: {
                language: '中文',
                outlineLength: '中等',
                moreRequirements: ''
            }
        };

        this.apiConfig = {
            backendUrl: 'http://localhost:8000',
            aiProvider: 'deepseek',
            apiKey: ''
        };

        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.loadSettings();
        this.bindEvents();
        this.updateUI();
        this.checkBackendConnection();
        this.loadTemplates();
    }

    /**
     * 加载本地设置
     */
    loadSettings() {
        const savedConfig = localStorage.getItem('aipptx-config');
        if (savedConfig) {
            try {
                const config = JSON.parse(savedConfig);
                this.apiConfig = { ...this.apiConfig, ...config };
                apiClient.setBaseURL(this.apiConfig.backendUrl);
            } catch (error) {
                console.error('Failed to load settings:', error);
            }
        }
    }

    /**
     * 保存设置到本地
     */
    saveSettings() {
        localStorage.setItem('aipptx-config', JSON.stringify(this.apiConfig));
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 导航按钮
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const step = parseInt(e.target.dataset.step);
                this.goToStep(step);
            });
        });

        // 步骤按钮
        this.bindStepButtons();

        // 输入类型切换
        this.bindInputTypeTabs();

        // 文件上传
        this.bindFileUpload();

        // 设置相关
        this.bindSettingsEvents();

        // 其他按钮
        this.bindOtherButtons();

        // 模板选择
        this.bindTemplateSelection();
    }

    /**
     * 绑定步骤按钮事件
     */
    bindStepButtons() {
        // 步骤1 - 下一步
        document.getElementById('btn-next-1')?.addEventListener('click', () => {
            this.handleStep1Next();
        });

        // 步骤2 - 上一步/下一步
        document.getElementById('btn-prev-2')?.addEventListener('click', () => {
            this.goToStep(1);
        });
        document.getElementById('btn-next-2')?.addEventListener('click', () => {
            this.goToStep(3);
        });
        document.getElementById('btn-regenerate-outline')?.addEventListener('click', () => {
            this.generateOutline();
        });

        // 步骤3 - 上一步/下一步
        document.getElementById('btn-prev-3')?.addEventListener('click', () => {
            this.goToStep(2);
        });
        document.getElementById('btn-next-3')?.addEventListener('click', () => {
            this.goToStep(4);
        });

        // 步骤4 - 上一步/重新开始
        document.getElementById('btn-prev-4')?.addEventListener('click', () => {
            this.goToStep(3);
        });
        document.getElementById('btn-restart-final')?.addEventListener('click', () => {
            this.restartProject();
        });
    }

    /**
     * 绑定输入类型标签页
     */
    bindInputTypeTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = e.target.dataset.type;
                this.switchInputType(type);
            });
        });
    }

    /**
     * 绑定文件上传
     */
    bindFileUpload() {
        const fileUpload = document.getElementById('file-upload');
        const fileInput = document.getElementById('file-input');

        if (fileUpload && fileInput) {
            // 点击上传区域
            fileUpload.addEventListener('click', () => {
                fileInput.click();
            });

            // 文件选择
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileUpload(file);
                }
            });

            // 拖拽上传
            fileUpload.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileUpload.classList.add('dragover');
            });

            fileUpload.addEventListener('dragleave', () => {
                fileUpload.classList.remove('dragover');
            });

            fileUpload.addEventListener('drop', (e) => {
                e.preventDefault();
                fileUpload.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
        }
    }

    /**
     * 绑定设置相关事件
     */
    bindSettingsEvents() {
        const settingsBtn = document.getElementById('btn-settings');
        const modal = document.getElementById('settings-modal');
        const modalClose = document.getElementById('modal-close');

        // 打开设置
        settingsBtn?.addEventListener('click', () => {
            this.openSettings();
        });

        // 关闭设置
        modalClose?.addEventListener('click', () => {
            this.closeSettings();
        });

        // 点击背景关闭
        modal?.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeSettings();
            }
        });

        // 设置标签页
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchSettingsTab(tabName);
            });
        });

        // 保存设置
        document.getElementById('btn-save-settings')?.addEventListener('click', () => {
            this.saveUserSettings();
        });

        // 测试连接
        document.getElementById('btn-test-connection')?.addEventListener('click', () => {
            this.testConnection();
        });
    }

    /**
     * 绑定其他按钮
     */
    bindOtherButtons() {
        // 重新开始
        document.getElementById('btn-restart')?.addEventListener('click', () => {
            this.restartProject();
        });

        // 下载PPT
        document.getElementById('btn-download')?.addEventListener('click', () => {
            this.downloadPPT();
        });
    }

    /**
     * 绑定模板选择
     */
    bindTemplateSelection() {
        // 这个方法会在模板加载后动态绑定事件
    }

    /**
     * 切换到指定步骤
     * @param {number} step 
     */
    goToStep(step) {
        if (step < 1 || step > 4) return;

        this.currentStep = step;
        this.updateUI();
        this.updateProgress();
    }

    /**
     * 更新UI界面
     */
    updateUI() {
        // 更新导航按钮状态
        document.querySelectorAll('.nav-btn').forEach(btn => {
            const step = parseInt(btn.dataset.step);
            btn.classList.toggle('active', step === this.currentStep);
        });

        // 显示对应步骤面板
        document.querySelectorAll('.step-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        const currentPanel = document.getElementById(`step-${this.currentStep}`);
        if (currentPanel) {
            currentPanel.classList.add('active');
        }

        // 更新状态显示
        this.updateStatusDisplay();

        // 更新技术信息
        this.updateTechInfo();
    }

    /**
     * 更新进度条
     */
    updateProgress() {
        const progressFill = document.getElementById('progress-fill');
        const percentage = Math.max(0, (this.currentStep - 1) / 4 * 100);
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }

        // 更新步骤图标和标签
        for (let i = 1; i <= 5; i++) {
            const icon = document.getElementById(`icon-${i}`);
            const step = document.querySelector(`[data-step="${i}"]`);
            
            if (!icon || !step) continue;

            const iconElement = icon;
            const labelElement = step.querySelector('.progress-step-label');

            // 移除所有状态类
            iconElement.classList.remove('completed', 'current', 'pending');
            labelElement?.classList.remove('completed', 'current', 'pending');

            if (i < this.currentStep) {
                // 已完成
                iconElement.classList.add('completed');
                labelElement?.classList.add('completed');
                iconElement.textContent = '✅';
            } else if (i === this.currentStep) {
                // 当前步骤
                iconElement.classList.add('current');
                labelElement?.classList.add('current');
                iconElement.textContent = '🔄';
            } else {
                // 待执行
                iconElement.classList.add('pending');
                labelElement?.classList.add('pending');
                const icons = ['📝', '🧠', '🎨', '⚡', '🎉'];
                iconElement.textContent = icons[i - 1] || '⏳';
            }
        }

        // 更新当前步骤显示
        const currentStepSpan = document.getElementById('current-step');
        if (currentStepSpan) {
            currentStepSpan.textContent = `${this.currentStep}/4`;
        }
    }

    /**
     * 更新状态显示
     */
    updateStatusDisplay() {
        const titleSpan = document.getElementById('status-title');
        const lengthSpan = document.getElementById('status-length');
        const outlineStatus = document.getElementById('status-outline');
        const templateStatus = document.getElementById('status-template');
        const pptStatus = document.getElementById('status-ppt');

        if (titleSpan) {
            titleSpan.textContent = this.projectData.title || '未设置';
        }

        if (lengthSpan) {
            lengthSpan.textContent = `${this.projectData.inputContent.length} 字符`;
        }

        if (outlineStatus) {
            outlineStatus.style.display = this.projectData.outlineContent ? 'block' : 'none';
        }

        if (templateStatus) {
            templateStatus.style.display = this.projectData.templateId ? 'block' : 'none';
        }

        if (pptStatus) {
            pptStatus.style.display = this.projectData.generatedFile ? 'block' : 'none';
        }
    }

    /**
     * 更新技术信息
     */
    updateTechInfo() {
        const backendUrlSpan = document.getElementById('backend-url');
        const aiProviderSpan = document.getElementById('ai-provider');

        if (backendUrlSpan) {
            backendUrlSpan.textContent = this.apiConfig.backendUrl;
        }

        if (aiProviderSpan) {
            const providerNames = {
                'openai': 'OpenAI',
                'deepseek': 'DeepSeek',
                'anthropic': 'Anthropic'
            };
            aiProviderSpan.textContent = providerNames[this.apiConfig.aiProvider] || this.apiConfig.aiProvider;
        }
    }

    /**
     * 切换输入类型
     * @param {string} type 
     */
    switchInputType(type) {
        this.projectData.inputType = type;

        // 更新标签页状态
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });

        // 显示对应面板
        document.querySelectorAll('.input-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        const activePanel = document.getElementById(`panel-${type}`);
        if (activePanel) {
            activePanel.classList.add('active');
        }
    }

    /**
     * 处理步骤1的下一步操作
     */
    async handleStep1Next() {
        const inputType = this.projectData.inputType;
        let content = '';
        let title = '';

        try {
            if (inputType === 'topic') {
                const textarea = document.getElementById('topic-input');
                content = textarea?.value.trim() || '';
                title = content.length > 20 ? content.substring(0, 20) + '...' : content;
            } else if (inputType === 'file') {
                if (!this.projectData.inputContent) {
                    this.showToast('请先上传文件', 'error');
                    return;
                }
                content = this.projectData.inputContent;
                title = this.projectData.title || '文件内容';
            } else if (inputType === 'url') {
                const urlInput = document.getElementById('url-input');
                const url = urlInput?.value.trim() || '';
                
                if (!url) {
                    this.showToast('请输入有效的网页链接', 'error');
                    return;
                }

                this.showToast('正在解析网页内容...', 'info');
                
                try {
                    const result = await apiClient.parseWebContent(url);
                    content = result.data.content;
                    title = result.data.title || '网页内容';
                    this.showToast('网页内容解析成功', 'success');
                } catch (error) {
                    this.showToast(`网页解析失败：${error.message}`, 'error');
                    return;
                }
            }

            if (!content) {
                this.showToast('请输入有效内容', 'error');
                return;
            }

            this.projectData.inputContent = content;
            this.projectData.title = title;

            this.goToStep(2);
            this.generateOutline();

        } catch (error) {
            console.error('Step 1 error:', error);
            this.showToast(`处理失败：${error.message}`, 'error');
        }
    }

    /**
     * 生成大纲
     */
    async generateOutline() {
        const loadingContainer = document.getElementById('outline-loading');
        const resultContainer = document.getElementById('outline-result');
        const nextBtn = document.getElementById('btn-next-2');

        if (loadingContainer) loadingContainer.style.display = 'block';
        if (resultContainer) resultContainer.style.display = 'none';
        if (nextBtn) nextBtn.disabled = true;

        try {
            const result = await apiClient.generateOutline({
                content: this.projectData.inputContent,
                settings: this.projectData.settings
            });

            this.projectData.outlineContent = result.data.outline;

            // 显示结果
            const outlineContentDiv = document.getElementById('outline-content');
            if (outlineContentDiv) {
                outlineContentDiv.innerHTML = this.formatOutline(this.projectData.outlineContent);
            }

            if (loadingContainer) loadingContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';
            if (nextBtn) nextBtn.disabled = false;

            this.updateStatusDisplay();
            this.showToast('大纲生成成功', 'success');

        } catch (error) {
            console.error('Generate outline error:', error);
            this.showToast(`大纲生成失败：${error.message}`, 'error');
            
            if (loadingContainer) loadingContainer.style.display = 'none';
        }
    }

    /**
     * 格式化大纲内容
     * @param {string} outline 
     * @returns {string}
     */
    formatOutline(outline) {
        if (!outline) return '';
        
        return outline
            .split('\n')
            .map(line => {
                const trimmed = line.trim();
                if (!trimmed) return '';
                
                if (trimmed.startsWith('#')) {
                    const level = (trimmed.match(/^#+/) || [''])[0].length;
                    const text = trimmed.replace(/^#+\s*/, '');
                    return `<h${Math.min(level + 2, 6)}>${text}</h${Math.min(level + 2, 6)}>`;
                } else if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
                    const text = trimmed.replace(/^[-*]\s*/, '');
                    return `<li>${text}</li>`;
                } else {
                    return `<p>${trimmed}</p>`;
                }
            })
            .join('\n')
            .replace(/(<li>.*?<\/li>\s*)+/g, '<ul>$&</ul>');
    }

    /**
     * 加载模板
     */
    async loadTemplates() {
        try {
            const result = await apiClient.getTemplates();
            const templates = result.data || [];
            
            this.renderTemplates(templates);
            
        } catch (error) {
            console.error('Load templates error:', error);
            this.showToast(`模板加载失败：${error.message}`, 'error');
        }
    }

    /**
     * 渲染模板列表
     * @param {Array} templates 
     */
    renderTemplates(templates) {
        const templateGrid = document.getElementById('template-grid');
        if (!templateGrid) return;

        templateGrid.innerHTML = '';

        templates.forEach(template => {
            const templateCard = document.createElement('div');
            templateCard.className = 'template-card';
            templateCard.dataset.templateId = template.id;

            templateCard.innerHTML = `
                <div class="template-preview" style="background: ${template.primary_color || '#f8f9fa'}">
                    <div style="font-size: 2rem;">${template.icon || '📄'}</div>
                </div>
                <div class="template-name">${template.name}</div>
                <div class="template-description">${template.description}</div>
            `;

            templateCard.addEventListener('click', () => {
                this.selectTemplate(template.id, templateCard);
            });

            templateGrid.appendChild(templateCard);
        });
    }

    /**
     * 选择模板
     * @param {number} templateId 
     * @param {Element} cardElement 
     */
    selectTemplate(templateId, cardElement) {
        // 移除其他选中状态
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });

        // 选中当前模板
        cardElement.classList.add('selected');
        this.projectData.templateId = templateId;

        // 启用下一步按钮
        const nextBtn = document.getElementById('btn-next-3');
        if (nextBtn) nextBtn.disabled = false;

        this.updateStatusDisplay();
        this.showToast('模板选择成功', 'success');
    }

    /**
     * 处理文件上传
     * @param {File} file 
     */
    async handleFileUpload(file) {
        const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            this.showToast('不支持的文件格式', 'error');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB
            this.showToast('文件大小不能超过10MB', 'error');
            return;
        }

        this.showToast('正在上传文件...', 'info');

        try {
            const result = await apiClient.uploadFile(file);
            
            this.projectData.inputContent = result.data.content;
            this.projectData.title = result.data.title || file.name;

            // 更新UI显示
            const fileUpload = document.getElementById('file-upload');
            if (fileUpload) {
                fileUpload.innerHTML = `
                    <div class="upload-success">
                        <div class="upload-icon">📄</div>
                        <p><strong>${file.name}</strong></p>
                        <p class="upload-hint">文件上传成功</p>
                    </div>
                `;
            }

            this.showToast('文件上传成功', 'success');

        } catch (error) {
            console.error('File upload error:', error);
            this.showToast(`文件上传失败：${error.message}`, 'error');
        }
    }

    /**
     * 生成PPT
     */
    async generatePPT() {
        if (this.currentStep !== 4) {
            this.goToStep(4);
        }

        const loadingContainer = document.getElementById('generate-loading');
        const resultContainer = document.getElementById('generate-result');
        const progressText = document.getElementById('generate-progress');

        if (loadingContainer) loadingContainer.style.display = 'block';
        if (resultContainer) resultContainer.style.display = 'none';

        try {
            // 更新进度文本
            if (progressText) progressText.textContent = '正在准备生成...';

            const result = await apiClient.generatePPT({
                title: this.projectData.title,
                content: this.projectData.inputContent,
                outline: this.projectData.outlineContent,
                templateId: this.projectData.templateId,
                settings: this.projectData.settings
            });

            this.projectData.generatedFile = result.data.filename;

            // 更新下载链接
            const downloadBtn = document.getElementById('btn-download');
            if (downloadBtn) {
                downloadBtn.href = `${this.apiConfig.backendUrl}/api/v1/files/download/${this.projectData.generatedFile}`;
                downloadBtn.download = this.projectData.generatedFile;
            }

            if (loadingContainer) loadingContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';

            this.updateStatusDisplay();
            this.showToast('PPT生成成功', 'success');

        } catch (error) {
            console.error('Generate PPT error:', error);
            this.showToast(`PPT生成失败：${error.message}`, 'error');
            
            if (loadingContainer) loadingContainer.style.display = 'none';
        }
    }

    /**
     * 下载PPT
     */
    async downloadPPT() {
        if (!this.projectData.generatedFile) {
            this.showToast('没有可下载的文件', 'error');
            return;
        }

        try {
            const blob = await apiClient.downloadPPT(this.projectData.generatedFile);
            
            // 创建下载链接
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.projectData.generatedFile;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showToast('下载成功', 'success');

        } catch (error) {
            console.error('Download error:', error);
            this.showToast(`下载失败：${error.message}`, 'error');
        }
    }

    /**
     * 重新开始项目
     */
    restartProject() {
        if (confirm('确定要重新开始吗？这将清除所有当前数据。')) {
            this.currentStep = 1;
            this.projectData = {
                title: '',
                inputType: 'topic',
                inputContent: '',
                outlineContent: '',
                templateId: null,
                generatedFile: null,
                settings: {
                    language: '中文',
                    outlineLength: '中等',
                    moreRequirements: ''
                }
            };

            // 重置表单
            document.getElementById('topic-input').value = '';
            document.getElementById('url-input').value = '';
            
            // 重置文件上传区域
            const fileUpload = document.getElementById('file-upload');
            if (fileUpload) {
                fileUpload.innerHTML = `
                    <input type="file" id="file-input" accept=".pdf,.docx,.txt,.md" hidden>
                    <div class="upload-placeholder">
                        <div class="upload-icon">📁</div>
                        <p>点击或拖拽文件到此处</p>
                        <p class="upload-hint">支持 PDF、DOCX、TXT、MD 格式</p>
                    </div>
                `;
            }

            // 重新绑定文件上传事件
            this.bindFileUpload();

            // 移除模板选中状态
            document.querySelectorAll('.template-card').forEach(card => {
                card.classList.remove('selected');
            });

            this.switchInputType('topic');
            this.updateUI();
            this.updateProgress();
            this.showToast('项目已重置', 'success');
        }
    }

    /**
     * 打开设置弹窗
     */
    openSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) {
            modal.classList.add('show');
            
            // 填充当前设置值
            const backendUrlInput = document.getElementById('backend-url-input');
            const aiProviderSelect = document.getElementById('ai-provider-select');
            const apiKeyInput = document.getElementById('api-key-input');

            if (backendUrlInput) backendUrlInput.value = this.apiConfig.backendUrl;
            if (aiProviderSelect) aiProviderSelect.value = this.apiConfig.aiProvider;
            if (apiKeyInput) apiKeyInput.value = this.apiConfig.apiKey;
        }
    }

    /**
     * 关闭设置弹窗
     */
    closeSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    /**
     * 切换设置标签页
     * @param {string} tabName 
     */
    switchSettingsTab(tabName) {
        // 更新标签状态
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // 显示对应面板
        document.querySelectorAll('.settings-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        const activePanel = document.getElementById(`settings-${tabName}`);
        if (activePanel) {
            activePanel.classList.add('active');
        }
    }

    /**
     * 保存用户设置
     */
    saveUserSettings() {
        const backendUrlInput = document.getElementById('backend-url-input');
        const aiProviderSelect = document.getElementById('ai-provider-select');
        const apiKeyInput = document.getElementById('api-key-input');

        this.apiConfig.backendUrl = backendUrlInput?.value || this.apiConfig.backendUrl;
        this.apiConfig.aiProvider = aiProviderSelect?.value || this.apiConfig.aiProvider;
        this.apiConfig.apiKey = apiKeyInput?.value || this.apiConfig.apiKey;

        // 更新API客户端配置
        apiClient.setBaseURL(this.apiConfig.backendUrl);

        // 保存到本地存储
        this.saveSettings();

        // 更新UI
        this.updateTechInfo();

        this.showToast('设置保存成功', 'success');
        this.closeSettings();
    }

    /**
     * 测试后端连接
     */
    async testConnection() {
        const backendUrl = document.getElementById('backend-url-input')?.value || this.apiConfig.backendUrl;
        
        this.showToast('正在测试连接...', 'info');

        try {
            // 临时设置URL进行测试
            const originalUrl = apiClient.baseURL;
            apiClient.setBaseURL(backendUrl);
            
            const result = await apiClient.healthCheck();
            
            // 恢复原URL
            apiClient.setBaseURL(originalUrl);
            
            this.showToast(`连接成功：${result.message || '服务正常'}`, 'success');

        } catch (error) {
            this.showToast(`连接失败：${error.message}`, 'error');
        }
    }

    /**
     * 检查后端连接状态
     */
    async checkBackendConnection() {
        try {
            await apiClient.healthCheck();
        } catch (error) {
            console.warn('Backend connection failed:', error);
            this.showToast('后端服务连接失败，请检查服务状态', 'warning');
        }
    }

    /**
     * 显示消息提示
     * @param {string} message 
     * @param {string} type 
     */
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastContent = document.getElementById('toast-content');

        if (!toast || !toastContent) return;

        toastContent.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');

        // 3秒后自动隐藏
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AIPPTXApp();
    
    // 如果是直接跳转到生成步骤，自动开始生成
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('action') === 'generate') {
        setTimeout(() => {
            window.app.generatePPT();
        }, 1000);
    }
});
