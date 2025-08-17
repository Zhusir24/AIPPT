/**
 * API 交互模块
 * 处理与 FastAPI 后端的所有通信
 */

class APIClient {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.config = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
    }

    /**
     * 设置后端URL
     * @param {string} url 
     */
    setBaseURL(url) {
        this.baseURL = url;
    }

    /**
     * 通用请求方法
     * @param {string} endpoint 
     * @param {Object} options 
     * @returns {Promise}
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...this.config,
            ...options,
            headers: {
                ...this.config.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * GET 请求
     * @param {string} endpoint 
     * @returns {Promise}
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST 请求
     * @param {string} endpoint 
     * @param {Object} data 
     * @returns {Promise}
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * 上传文件
     * @param {string} endpoint 
     * @param {FormData} formData 
     * @returns {Promise}
     */
    async upload(endpoint, formData) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('File Upload Error:', error);
            throw error;
        }
    }

    // ================== 健康检查 ==================
    /**
     * 检查后端服务健康状态
     * @returns {Promise}
     */
    async healthCheck() {
        return this.get('/health');
    }

    // ================== AI 相关接口 ==================
    /**
     * 获取AI提供商信息
     * @returns {Promise}
     */
    async getAIProvider() {
        return this.get('/api/v1/ai/provider');
    }

    /**
     * 生成大纲
     * @param {Object} data 
     * @returns {Promise}
     */
    async generateOutline(data) {
        return this.post('/api/v1/ai/generate-outline', data);
    }

    /**
     * 生成PPT
     * @param {Object} data 
     * @returns {Promise}
     */
    async generatePPT(data) {
        return this.post('/api/v1/ai/generate-ppt', data);
    }

    // ================== 文件相关接口 ==================
    /**
     * 上传文件
     * @param {File} file 
     * @returns {Promise}
     */
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this.upload('/api/v1/files/upload', formData);
    }

    /**
     * 解析网页内容
     * @param {string} url 
     * @returns {Promise}
     */
    async parseWebContent(url) {
        return this.post('/api/v1/files/extract-url', { url });
    }

    /**
     * 下载生成的PPT
     * @param {string} filename 
     * @returns {Promise<Blob>}
     */
    async downloadPPT(filename) {
        const url = `${this.baseURL}/api/v1/files/download/${filename}`;
        
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.blob();
        } catch (error) {
            console.error('Download Error:', error);
            throw error;
        }
    }

    // ================== 模板相关接口 ==================
    /**
     * 获取所有模板
     * @returns {Promise}
     */
    async getTemplates() {
        return this.get('/api/v1/templates/');
    }

    /**
     * 获取模板详情
     * @param {number} templateId 
     * @returns {Promise}
     */
    async getTemplate(templateId) {
        return this.get(`/api/v1/templates/${templateId}`);
    }

    // ================== API配置相关接口 ==================
    /**
     * 测试API配置连接
     * @param {Object} config - API配置对象
     * @returns {Promise}
     */
    async testAPIConfig(config) {
        return this.post('/api/v1/ai/test-api-config', config);
    }

    /**
     * 保存API配置
     * @param {Object} config - API配置对象
     * @returns {Promise}
     */
    async saveAPIConfig(config) {
        return this.post('/api/v1/ai/save-api-config', config);
    }

    // ================== 项目相关接口 ==================
    /**
     * 创建项目
     * @param {Object} data 
     * @returns {Promise}
     */
    async createProject(data) {
        return this.post('/api/v1/projects/', data);
    }

    /**
     * 获取项目列表
     * @returns {Promise}
     */
    async getProjects() {
        return this.get('/api/v1/projects/');
    }

    /**
     * 获取项目详情
     * @param {number} projectId 
     * @returns {Promise}
     */
    async getProject(projectId) {
        return this.get(`/api/v1/projects/${projectId}`);
    }

    /**
     * 更新项目
     * @param {number} projectId 
     * @param {Object} data 
     * @returns {Promise}
     */
    async updateProject(projectId, data) {
        return this.request(`/api/v1/projects/${projectId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * 删除项目
     * @param {number} projectId 
     * @returns {Promise}
     */
    async deleteProject(projectId) {
        return this.request(`/api/v1/projects/${projectId}`, {
            method: 'DELETE'
        });
    }
}

// 创建全局API客户端实例
window.apiClient = new APIClient();

// 导出用于模块化使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}
