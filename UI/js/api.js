/**
 * API Client cho Test Case AI Agent
 */

class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    /**
     * Thực hiện HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * Lấy tất cả requests
     */
    async getAllRequests() {
        return await this.request('/requests');
    }

    /**
     * Tạo request mới
     */
    async createRequest(title, pbiRequirement) {
        return await this.request('/requests', {
            method: 'POST',
            body: JSON.stringify({
                title: title,
                pbi_requirement: pbiRequirement
            })
        });
    }

    /**
     * Lấy request theo conversation_id
     */
    async getRequest(conversationId) {
        return await this.request(`/requests/${conversationId}`);
    }

    /**
     * Lấy messages của conversation
     */
    async getMessages(conversationId) {
        return await this.request(`/requests/${conversationId}/messages`);
    }

    /**
     * Xóa request
     */
    async deleteRequest(conversationId) {
        return await this.request(`/requests/${conversationId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Gửi request tới agent với streaming
     */
    async sendToAgent(conversationId, title, pbiRequirement, fileAttachment = null) {
        const formData = new FormData();
        formData.append('conversation_id', conversationId);
        formData.append('title', title);
        formData.append('pbi_requirement', pbiRequirement);
        
        if (fileAttachment) {
            formData.append('file_attachment', fileAttachment);
        }

        const response = await fetch(`${this.baseURL}/agent-testcase`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response;
    }
}

// Export singleton instance
const apiClient = new APIClient();
