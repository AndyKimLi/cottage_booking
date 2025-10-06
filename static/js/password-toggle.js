/**
 * Компонент для показа/скрытия пароля
 */
class PasswordToggle {
    constructor(inputId, options = {}) {
        this.input = document.getElementById(inputId);
        if (!this.input) return;
        
        this.options = {
            showIcon: 'fas fa-eye',
            hideIcon: 'fas fa-eye-slash',
            toggleClass: 'password-toggle',
            ...options
        };
        
        this.isVisible = false;
        this.init();
    }
    
    init() {
        // Создаем контейнер для input и кнопки
        const container = document.createElement('div');
        container.className = 'password-toggle-container position-relative';
        
        // Перемещаем input в контейнер
        this.input.parentNode.insertBefore(container, this.input);
        container.appendChild(this.input);
        
        // Добавляем кнопку переключения
        this.toggleButton = document.createElement('button');
        this.toggleButton.type = 'button';
        this.toggleButton.className = `btn btn-link ${this.options.toggleClass}`;
        this.toggleButton.innerHTML = `<i class="${this.options.showIcon}"></i>`;
        this.toggleButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            border: none;
            background: none;
            color: #6c757d;
            padding: 0;
            z-index: 10;
        `;
        
        container.appendChild(this.toggleButton);
        
        // Добавляем отступ для input, чтобы текст не перекрывался с кнопкой
        this.input.style.paddingRight = '40px';
        
        // Обработчик клика
        this.toggleButton.addEventListener('click', () => this.toggle());
    }
    
    toggle() {
        this.isVisible = !this.isVisible;
        
        if (this.isVisible) {
            this.input.type = 'text';
            this.toggleButton.innerHTML = `<i class="${this.options.hideIcon}"></i>`;
            this.toggleButton.title = 'Скрыть пароль';
        } else {
            this.input.type = 'password';
            this.toggleButton.innerHTML = `<i class="${this.options.showIcon}"></i>`;
            this.toggleButton.title = 'Показать пароль';
        }
    }
}

// Автоматическая инициализация всех полей пароля
document.addEventListener('DOMContentLoaded', function() {
    // Находим все поля пароля
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    
    passwordInputs.forEach((input, index) => {
        // Создаем уникальный ID если его нет
        if (!input.id) {
            input.id = `password_${index}`;
        }
        
        // Инициализируем компонент
        new PasswordToggle(input.id);
    });
});

// Функция для ручной инициализации
function initPasswordToggle(inputId, options = {}) {
    return new PasswordToggle(inputId, options);
}
