document.addEventListener('DOMContentLoaded', function() {
    // Обработка добавления в корзину через AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.action;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем счетчик корзины
                    const cartBadge = document.querySelector('.cart-badge');
                    if (cartBadge) {
                        cartBadge.textContent = data.cart_count;
                    }
                    
                    // Показываем сообщение
                    showMessage(data.message, 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Ошибка при добавлении в корзину', 'error');
            });
        });
    });
    
    function showMessage(message, type) {
        // Создаем и показываем всплывающее сообщение
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.container').prepend(alertDiv);
        
        // Автоматически скрываем через 3 секунды
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
});