/**
 * Utility functions cho Test Case AI Agent
 */

/**
 * Format datetime string
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format relative time (e.g., "2 giờ trước")
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Vừa xong';
    if (diffMins < 60) return `${diffMins} phút trước`;
    if (diffHours < 24) return `${diffHours} giờ trước`;
    if (diffDays < 7) return `${diffDays} ngày trước`;
    
    return formatDateTime(dateString);
}

/**
 * Truncate text với ellipsis
 */
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Generate unique ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show loading state
 */
function showLoading(element) {
    element.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(element, message) {
    element.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">❌</div>
            <div class="empty-state-title">Có lỗi xảy ra</div>
            <div class="empty-state-description">${message}</div>
        </div>
    `;
}

/**
 * Show empty state
 */
function showEmptyState(element, title, description, actionButton = null) {
    let actionHtml = '';
    if (actionButton) {
        actionHtml = `<button class="btn btn-primary" onclick="${actionButton.onclick}">${actionButton.text}</button>`;
    }

    element.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div class="empty-state-title">${title}</div>
            <div class="empty-state-description">${description}</div>
            ${actionHtml}
        </div>
    `;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Add toast styles if not exists
    if (!document.querySelector('#toast-styles')) {
        const styles = document.createElement('style');
        styles.id = 'toast-styles';
        styles.textContent = `
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                animation: slideIn 0.3s ease;
                max-width: 400px;
            }
            .toast-success { border-left: 4px solid #28a745; }
            .toast-error { border-left: 4px solid #dc3545; }
            .toast-warning { border-left: 4px solid #ffc107; }
            .toast-info { border-left: 4px solid #17a2b8; }
            .toast-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
            }
            .toast-message {
                flex: 1;
                margin-right: 10px;
            }
            .toast-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #666;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }

    // Add to DOM
    document.body.appendChild(toast);

    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }
}

/**
 * Confirm dialog
 */
function confirmDialog(message, onConfirm, onCancel = null) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3>Xác nhận</h3>
            </div>
            <div class="modal-body">
                <p>${message}</p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">Hủy</button>
                <button class="btn btn-danger" onclick="confirmAction()">Xác nhận</button>
            </div>
        </div>
    `;

    // Add modal styles if not exists
    if (!document.querySelector('#modal-styles')) {
        const styles = document.createElement('style');
        styles.id = 'modal-styles';
        styles.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            .modal {
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
                animation: modalIn 0.3s ease;
            }
            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #e9ecef;
            }
            .modal-header h3 {
                margin: 0;
                color: #333;
            }
            .modal-body {
                padding: 20px;
            }
            .modal-footer {
                padding: 15px 20px;
                border-top: 1px solid #e9ecef;
                display: flex;
                justify-content: flex-end;
                gap: 10px;
            }
            @keyframes modalIn {
                from { transform: scale(0.8); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }

    // Add global functions
    window.closeModal = () => {
        overlay.remove();
        if (onCancel) onCancel();
    };

    window.confirmAction = () => {
        overlay.remove();
        onConfirm();
    };

    document.body.appendChild(overlay);
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Đã sao chép vào clipboard', 'success');
    } catch (err) {
        console.error('Failed to copy: ', err);
        showToast('Không thể sao chép', 'error');
    }
}

/**
 * Download text as file
 */
function downloadAsFile(content, filename, contentType = 'text/plain') {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Validate form data
 */
function validateForm(formData) {
    const errors = [];
    
    if (!formData.title || formData.title.trim().length < 3) {
        errors.push('Tiêu đề phải có ít nhất 3 ký tự');
    }
    
    if (!formData.pbi_requirement || formData.pbi_requirement.trim().length < 10) {
        errors.push('Yêu cầu PBI phải có ít nhất 10 ký tự');
    }
    
    return errors;
}
