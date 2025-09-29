// Função para fechar alertas automaticamente
document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = '#e1e5e9';
                }
            });

            if (!isValid) {
                e.preventDefault();
                showAlert('Por favor, preencha todos os campos obrigatórios.', 'danger');
            }
        });
    });
});

// Função para mostrar alertas dinamicamente
function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.flash-messages') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas fa-info-circle"></i>
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, 5000);
}

function createAlertsContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.querySelector('.main-content').insertBefore(container, document.querySelector('.main-content').firstChild);
    return container;
}

// Função para confirmar exclusões
function confirmDelete(message = 'Tem certeza que deseja excluir este item?') {
    return confirm(message);
}