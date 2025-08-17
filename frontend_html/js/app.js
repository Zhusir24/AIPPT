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
            },
            // 步骤完成状态
            stepCompleted: {
                step1: false,  // 输入内容
                step2: false,  // 生成大纲
                step3: false,  // 选择模板
                step4: false   // 生成PPT
            }
        };

        this.apiConfig = {
            backendUrl: 'http://localhost:8000',
            aiProvider: 'deepseek',
            apiKey: '',
            // 自定义API配置
            customApiUrl: '',
            customModelName: '',
            customApiKey: ''
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
        this.updateNavigationState(); // 初始化导航状态
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
                // 检查按钮是否被禁用
                if (e.target.classList.contains('disabled') || e.target.disabled) {
                    e.preventDefault();
                    return;
                }
                
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

        // AI提供商选择变化
        document.getElementById('ai-provider-select')?.addEventListener('change', (e) => {
            this.handleProviderChange(e.target.value);
        });
    }

    /**
     * 处理AI提供商选择变化
     * @param {string} provider 
     */
    handleProviderChange(provider) {
        const standardApiKeyGroup = document.getElementById('standard-api-key-group');
        const customApiConfig = document.getElementById('custom-api-config');
        
        if (provider === 'custom') {
            // 显示自定义配置，隐藏标准API密钥
            if (standardApiKeyGroup) standardApiKeyGroup.style.display = 'none';
            if (customApiConfig) customApiConfig.style.display = 'block';
        } else {
            // 显示标准API密钥，隐藏自定义配置
            if (standardApiKeyGroup) standardApiKeyGroup.style.display = 'block';
            if (customApiConfig) customApiConfig.style.display = 'none';
        }
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
     * 检查步骤是否可以访问
     * @param {number} step 
     * @returns {boolean}
     */
    canAccessStep(step) {
        if (step === 1) return true; // 第一步总是可以访问
        
        // 检查前面的步骤是否都已完成
        for (let i = 1; i < step; i++) {
            if (!this.projectData.stepCompleted[`step${i}`]) {
                return false;
            }
        }
        return true;
    }

    /**
     * 标记步骤为完成
     * @param {number} step 
     */
    markStepCompleted(step) {
        this.projectData.stepCompleted[`step${step}`] = true;
        this.updateNavigationState();
    }

    /**
     * 切换到指定步骤
     * @param {number} step 
     */
    goToStep(step) {
        if (step < 1 || step > 4) return;

        // 检查步骤是否可以访问
        if (!this.canAccessStep(step)) {
            const stepNames = ['', '输入内容', '生成大纲', '选择模板', '生成PPT'];
            this.showToast(`请先完成前面的步骤再访问"${stepNames[step]}"`, 'warning');
            return;
        }

        this.currentStep = step;
        this.updateUI();
        this.updateProgress();

        // 如果进入步骤4（生成PPT），自动开始生成
        if (step === 4) {
            console.log('🎯 进入步骤4，检查自动生成PPT条件');
            console.log('📋 检查数据:', {
                hasOutline: !!this.projectData.outlineContent,
                hasTemplate: !!this.projectData.templateId,
                outlineLength: this.projectData.outlineContent ? this.projectData.outlineContent.length : 0,
                templateId: this.projectData.templateId
            });
            
            if (this.projectData.outlineContent && this.projectData.templateId) {
                console.log('✅ 条件满足，500ms后自动开始生成PPT');
                setTimeout(() => {
                    console.log('⏰ 延迟时间到，开始调用generatePPT');
                    this.generatePPT();
                }, 500); // 稍微延迟以确保UI更新完成
            } else {
                console.log('❌ 条件不满足，不会自动生成PPT');
                if (!this.projectData.outlineContent) {
                    console.log('  - 缺少大纲内容');
                }
                if (!this.projectData.templateId) {
                    console.log('  - 缺少模板选择');
                }
            }
        }
    }

    /**
     * 更新导航状态
     */
    updateNavigationState() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            const step = parseInt(btn.dataset.step);
            const canAccess = this.canAccessStep(step);
            
            // 设置按钮可用状态
            btn.disabled = !canAccess;
            btn.classList.toggle('disabled', !canAccess);
            btn.classList.toggle('active', step === this.currentStep);
            
            // 添加提示
            if (!canAccess) {
                btn.title = '请先完成前面的步骤';
            } else {
                btn.title = '';
            }
        });
    }

    /**
     * 更新UI界面
     */
    updateUI() {
        // 更新导航按钮状态
        this.updateNavigationState();

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
                'anthropic': 'Anthropic',
                'custom': '自定义兼容'
            };
            
            let displayName = providerNames[this.apiConfig.aiProvider] || this.apiConfig.aiProvider;
            
            // 如果是自定义提供商，显示模型名称
            if (this.apiConfig.aiProvider === 'custom' && this.apiConfig.customModelName) {
                displayName += ` (${this.apiConfig.customModelName})`;
            }
            
            aiProviderSpan.textContent = displayName;
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

            // 标记步骤1完成
            this.markStepCompleted(1);

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
                topic: this.projectData.inputContent,
                language: this.projectData.settings.language || '中文',
                outline_length: this.projectData.settings.outlineLength || '中等',
                additional_requirements: this.projectData.settings.moreRequirements || null
            });

            this.projectData.outlineContent = result.outline_markdown;

            // 显示结果
            const outlineContentDiv = document.getElementById('outline-content');
            if (outlineContentDiv) {
                outlineContentDiv.innerHTML = this.formatOutline(this.projectData.outlineContent);
            }

            if (loadingContainer) loadingContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';
            if (nextBtn) nextBtn.disabled = false;

            // 标记步骤2完成
            this.markStepCompleted(2);

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
            const templates = await apiClient.getTemplates();
            
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
    async selectTemplate(templateId, cardElement) {
        this.showToast('正在获取模板详情...', 'info');
        
        try {
            // 调用后端API获取模板详情
            const templateDetail = await apiClient.getTemplate(templateId);
            console.log('📋 获取到模板详情:', templateDetail);
            
            // 移除其他选中状态
            document.querySelectorAll('.template-card').forEach(card => {
                card.classList.remove('selected');
            });

            // 选中当前模板
            cardElement.classList.add('selected');
            this.projectData.templateId = templateId;
            this.projectData.templateDetail = templateDetail; // 保存模板详情

            // 启用下一步按钮
            const nextBtn = document.getElementById('btn-next-3');
            if (nextBtn) nextBtn.disabled = false;

            // 标记步骤3完成
            this.markStepCompleted(3);

            this.updateStatusDisplay();
            this.showToast(`模板选择成功：${templateDetail.name}`, 'success');
            
        } catch (error) {
            console.error('获取模板详情失败:', error);
            this.showToast(`模板选择失败：${error.message}`, 'error');
        }
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
            
            this.projectData.inputContent = result.extracted_content;
            this.projectData.title = file.name;

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
        console.log('🚀 开始生成PPT方法调用');
        console.log('📋 当前项目数据:', {
            outlineLength: this.projectData.outlineContent ? this.projectData.outlineContent.length : 0,
            templateId: this.projectData.templateId,
            currentStep: this.currentStep
        });
        
        if (this.currentStep !== 4) {
            console.log('🔄 当前不在步骤4，跳转到步骤4');
            this.goToStep(4);
        }

        // 验证必要数据
        if (!this.projectData.outlineContent) {
            console.error('❌ 缺少大纲内容');
            this.showToast('缺少大纲内容，请先生成大纲', 'error');
            return;
        }
        
        if (!this.projectData.templateId) {
            console.error('❌ 缺少模板ID');
            this.showToast('缺少模板选择，请先选择模板', 'error');
            return;
        }

        const loadingContainer = document.getElementById('generate-loading');
        const resultContainer = document.getElementById('generate-result');
        const progressText = document.getElementById('generate-progress');

        if (loadingContainer) loadingContainer.style.display = 'block';
        if (resultContainer) resultContainer.style.display = 'none';

        try {
            // 更新进度文本
            if (progressText) progressText.textContent = '正在准备生成...';

            console.log('📤 发送PPT生成请求到后端...');
            const requestData = {
                outline: this.projectData.outlineContent,
                template_id: this.projectData.templateId
            };
            console.log('📦 请求数据:', {
                outlineLength: requestData.outline.length,
                templateId: requestData.template_id
            });

            const result = await apiClient.generatePPT(requestData);
            console.log('✅ PPT生成成功，结果:', result);

            // 处理后端返回的BaseResponse格式
            const pptData = result.data || result;
            this.projectData.generatedFile = pptData.filename || pptData.file_path;

            // 更新下载链接
            const downloadBtn = document.getElementById('btn-download');
            if (downloadBtn) {
                downloadBtn.href = `${this.apiConfig.backendUrl}/api/v1/files/download/${this.projectData.generatedFile}`;
                downloadBtn.download = this.projectData.generatedFile;
            }

            if (loadingContainer) loadingContainer.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'block';

            // 标记步骤4完成
            this.markStepCompleted(4);

            this.updateStatusDisplay();
            this.showToast('PPT生成成功', 'success');

        } catch (error) {
            console.error('❌ PPT生成失败:', error);
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
                },
                // 重置步骤完成状态
                stepCompleted: {
                    step1: false,
                    step2: false,
                    step3: false,
                    step4: false
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
            
            // 自定义API配置字段
            const customApiUrl = document.getElementById('custom-api-url');
            const customModelName = document.getElementById('custom-model-name');
            const customApiKey = document.getElementById('custom-api-key');

            if (backendUrlInput) backendUrlInput.value = this.apiConfig.backendUrl;
            if (aiProviderSelect) aiProviderSelect.value = this.apiConfig.aiProvider;
            if (apiKeyInput) apiKeyInput.value = this.apiConfig.apiKey;
            
            // 填充自定义配置
            if (customApiUrl) customApiUrl.value = this.apiConfig.customApiUrl;
            if (customModelName) customModelName.value = this.apiConfig.customModelName;
            if (customApiKey) customApiKey.value = this.apiConfig.customApiKey;
            
            // 根据当前选择的提供商显示/隐藏相应字段
            this.handleProviderChange(this.apiConfig.aiProvider);
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
    async saveUserSettings() {
        this.showToast('正在保存设置...', 'info');

        try {
            const backendUrlInput = document.getElementById('backend-url-input');
            const aiProviderSelect = document.getElementById('ai-provider-select');
            const apiKeyInput = document.getElementById('api-key-input');
            
            // 自定义API配置字段
            const customApiUrl = document.getElementById('custom-api-url');
            const customModelName = document.getElementById('custom-model-name');
            const customApiKey = document.getElementById('custom-api-key');

            this.apiConfig.backendUrl = backendUrlInput?.value || this.apiConfig.backendUrl;
            this.apiConfig.aiProvider = aiProviderSelect?.value || this.apiConfig.aiProvider;
            this.apiConfig.apiKey = apiKeyInput?.value || this.apiConfig.apiKey;
            
            // 保存自定义配置
            this.apiConfig.customApiUrl = customApiUrl?.value || this.apiConfig.customApiUrl;
            this.apiConfig.customModelName = customModelName?.value || this.apiConfig.customModelName;
            this.apiConfig.customApiKey = customApiKey?.value || this.apiConfig.customApiKey;

            // 更新API客户端配置
            apiClient.setBaseURL(this.apiConfig.backendUrl);

            // 构建API配置对象发送到后端
            let effectiveApiKey = this.apiConfig.apiKey;
            const configToSave = {
                provider: this.apiConfig.aiProvider,
                api_key: effectiveApiKey
            };

            // 如果是自定义配置，添加额外参数和使用自定义API密钥
            if (this.apiConfig.aiProvider === 'custom') {
                if (this.apiConfig.customApiUrl && this.apiConfig.customModelName && this.apiConfig.customApiKey) {
                    configToSave.custom_api_url = this.apiConfig.customApiUrl;
                    configToSave.custom_model_name = this.apiConfig.customModelName;
                    configToSave.api_key = this.apiConfig.customApiKey;
                } else {
                    this.showToast('自定义API配置不完整', 'warning');
                }
            }

            // 如果有API密钥，则发送到后端保存并记录日志
            if (configToSave.api_key) {
                console.log('正在保存API配置到后端:', {
                    provider: configToSave.provider,
                    custom_api_url: configToSave.custom_api_url,
                    custom_model_name: configToSave.custom_model_name
                });

                try {
                    const result = await apiClient.saveAPIConfig(configToSave);
                    if (result.success) {
                        console.log('API配置保存成功:', result.data);
                    }
                } catch (error) {
                    console.warn('后端配置保存失败，但本地设置已保存:', error.message);
                }
            }

            // 保存到本地存储
            this.saveSettings();

            // 更新UI
            this.updateTechInfo();

            this.showToast('设置保存成功', 'success');
            this.closeSettings();

        } catch (error) {
            console.error('保存设置失败:', error);
            this.showToast(`保存失败: ${error.message}`, 'error');
        }
    }

    /**
     * 测试API配置连接
     */
    async testConnection() {
        this.showToast('正在测试API连接...', 'info');

        try {
            // 获取当前设置的API配置
            const aiProvider = document.getElementById('ai-provider-select')?.value || this.apiConfig.aiProvider;
            const apiKey = document.getElementById('api-key-input')?.value || this.apiConfig.apiKey;
            const customApiUrl = document.getElementById('custom-api-url')?.value || this.apiConfig.customApiUrl;
            const customModelName = document.getElementById('custom-model-name')?.value || this.apiConfig.customModelName;
            const customApiKey = document.getElementById('custom-api-key')?.value || this.apiConfig.customApiKey;

            // 验证必要字段
            let effectiveApiKey = apiKey;
            if (aiProvider === 'custom') {
                if (!customApiUrl || !customModelName || !customApiKey) {
                    this.showToast('自定义API配置不完整，请填写API地址、模型名称和API密钥', 'error');
                    return;
                }
                effectiveApiKey = customApiKey;
            } else if (!effectiveApiKey) {
                this.showToast('请先输入API密钥', 'error');
                return;
            }

            // 构建测试配置
            const testConfig = {
                provider: aiProvider,
                api_key: effectiveApiKey,
                test_message: "你好，这是一个连接测试，请简单回复。"
            };

            // 如果是自定义配置，添加额外参数
            if (aiProvider === 'custom') {
                testConfig.custom_api_url = customApiUrl;
                testConfig.custom_model_name = customModelName;
            }

            console.log('正在测试API配置:', {
                provider: testConfig.provider,
                custom_api_url: testConfig.custom_api_url,
                custom_model_name: testConfig.custom_model_name
            });

            // 调用后端测试API
            const result = await apiClient.testAPIConfig(testConfig);

            if (result.success) {
                const details = [
                    `✅ 连接成功！`,
                    `🤖 提供商: ${result.provider}`,
                    `📋 模型: ${result.model_name}`,
                    `⚡ 延迟: ${result.latency}ms`,
                    result.response_preview ? `💬 响应预览: ${result.response_preview}` : ''
                ].filter(Boolean).join('\n');
                
                this.showToast(details, 'success');
            } else {
                this.showToast(`❌ 连接失败: ${result.message}`, 'error');
            }

        } catch (error) {
            console.error('API配置测试失败:', error);
            this.showToast(`❌ 测试失败: ${error.message}`, 'error');
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
