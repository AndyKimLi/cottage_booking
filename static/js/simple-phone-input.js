/**
 * Простой компонент для ввода номера телефона (только цифры)
 */
class SimplePhoneInput {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.options = {
            placeholder: 'Введите номер телефона',
            maxLength: 15,
            ...options
        };
        
        this.hiddenInput = null;
        this.init();
    }
    
    init() {
        this.createHTML();
        this.bindEvents();
    }
    
    createHTML() {
        this.container.innerHTML = `
            <div class="simple-phone-container">
                <input type="tel" class="form-control" id="${this.container.id}_number" 
                       placeholder="${this.options.placeholder}" 
                       maxlength="${this.options.maxLength}">
                <input type="hidden" id="${this.container.id}_full" name="phone">
            </div>
        `;
        
        this.hiddenInput = this.container.querySelector(`#${this.container.id}_full`);
    }
    
    bindEvents() {
        const numberInput = this.container.querySelector(`#${this.container.id}_number`);
        
        numberInput.addEventListener('input', (e) => {
            // Разрешаем цифры, пробелы, дефисы, скобки и знак +
            let value = e.target.value.replace(/[^\d\s\-\(\)\+]/g, '');
            
            // Ограничиваем длину
            if (value.length > this.options.maxLength) {
                value = value.substring(0, this.options.maxLength);
            }
            
            e.target.value = value;
            this.updateHiddenInput(value);
        });
        
        numberInput.addEventListener('blur', () => {
            this.validatePhone();
        });
        
        // Предотвращаем ввод недопустимых символов
        numberInput.addEventListener('keypress', (e) => {
            if (!/[\d\s\-\(\)\+]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    updateHiddenInput(phoneNumber) {
        if (this.hiddenInput) {
            // Сохраняем номер как есть, без добавления +7
            this.hiddenInput.value = phoneNumber || '';
        }
    }
    
    validatePhone() {
        const numberInput = this.container.querySelector(`#${this.container.id}_number`);
        const phoneNumber = numberInput.value;
        const isValid = this.isValidPhone(phoneNumber);
        
        if (phoneNumber && !isValid) {
            numberInput.classList.add('is-invalid');
            numberInput.classList.remove('is-valid');
        } else if (phoneNumber && isValid) {
            numberInput.classList.add('is-valid');
            numberInput.classList.remove('is-invalid');
        } else {
            numberInput.classList.remove('is-valid', 'is-invalid');
        }
        
        return isValid;
    }
    
    isValidPhone(phoneNumber) {
        if (!phoneNumber) return true; // Пустой номер разрешен
        
        // Убираем все символы кроме цифр для проверки длины
        const digitsOnly = phoneNumber.replace(/\D/g, '');
        
        // Минимальная длина номера - 7 цифр, максимальная - 15
        return digitsOnly.length >= 7 && digitsOnly.length <= 15;
    }
    
    getValue() {
        return this.hiddenInput ? this.hiddenInput.value : '';
    }
    
    setValue(phone) {
        if (!phone) return;
        
        // Устанавливаем номер как есть
        const numberInput = this.container.querySelector(`#${this.container.id}_number`);
        if (numberInput) {
            numberInput.value = phone;
            this.updateHiddenInput(phone);
        }
    }
}

// Инициализация всех простых компонентов телефона на странице
document.addEventListener('DOMContentLoaded', function() {
    const phoneContainers = document.querySelectorAll('.simple-phone-input');
    phoneContainers.forEach(container => {
        new SimplePhoneInput(container.id);
    });
});
