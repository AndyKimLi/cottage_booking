/**
 * Компонент для раздельного ввода кода страны и номера телефона
 */
class PhoneInput {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.options = {
            defaultCountry: '+7',
            countries: [
                { code: '+7', name: 'Россия', flag: '🇷🇺' },
                { code: '+380', name: 'Украина', flag: '🇺🇦' },
                { code: '+375', name: 'Беларусь', flag: '🇧🇾' },
                { code: '+7', name: 'Казахстан', flag: '🇰🇿' },
                { code: '+998', name: 'Узбекистан', flag: '🇺🇿' },
                { code: '+86', name: 'Китай', flag: '🇨🇳' },
                { code: '+1', name: 'США/Канада', flag: '🇺🇸' },
                { code: '+44', name: 'Великобритания', flag: '🇬🇧' },
                { code: '+49', name: 'Германия', flag: '🇩🇪' },
                { code: '+33', name: 'Франция', flag: '🇫🇷' },
                { code: '+39', name: 'Италия', flag: '🇮🇹' },
                { code: '+34', name: 'Испания', flag: '🇪🇸' },
                { code: '+81', name: 'Япония', flag: '🇯🇵' },
                { code: '+82', name: 'Корея', flag: '🇰🇷' },
                { code: '+91', name: 'Индия', flag: '🇮🇳' },
                { code: '+90', name: 'Турция', flag: '🇹🇷' },
                { code: '+971', name: 'ОАЭ', flag: '🇦🇪' },
                { code: '+966', name: 'Саудовская Аравия', flag: '🇸🇦' },
                { code: '+20', name: 'Египет', flag: '🇪🇬' },
                { code: '+27', name: 'ЮАР', flag: '🇿🇦' }
            ],
            ...options
        };
        
        this.countryCode = this.options.defaultCountry;
        this.phoneNumber = '';
        this.hiddenInput = null;
        
        this.init();
    }
    
    init() {
        this.createHTML();
        this.bindEvents();
        this.updateHiddenInput();
    }
    
    createHTML() {
        this.container.innerHTML = `
            <div class="phone-input-container">
                <div class="input-group">
                    <select class="form-select" id="${this.container.id}_country" style="max-width: 120px;">
                        ${this.options.countries.map(country => 
                            `<option value="${country.code}" ${country.code === this.countryCode ? 'selected' : ''}>
                                ${country.flag} ${country.code}
                            </option>`
                        ).join('')}
                    </select>
                    <input type="tel" class="form-control" id="${this.container.id}_number" 
                           placeholder="999 123 45 67" maxlength="15">
                </div>
                <input type="hidden" id="${this.container.id}_full" name="phone">
            </div>
        `;
        
        this.hiddenInput = this.container.querySelector(`#${this.container.id}_full`);
    }
    
    bindEvents() {
        const countrySelect = this.container.querySelector(`#${this.container.id}_country`);
        const numberInput = this.container.querySelector(`#${this.container.id}_number`);
        
        countrySelect.addEventListener('change', (e) => {
            this.countryCode = e.target.value;
            this.updateHiddenInput();
        });
        
        numberInput.addEventListener('input', (e) => {
            // Очищаем от всех символов кроме цифр
            this.phoneNumber = e.target.value.replace(/\D/g, '');
            e.target.value = this.phoneNumber;
            this.updateHiddenInput();
        });
        
        numberInput.addEventListener('blur', () => {
            this.validatePhone();
        });
    }
    
    updateHiddenInput() {
        if (this.hiddenInput) {
            const fullPhone = this.phoneNumber ? `${this.countryCode}${this.phoneNumber}` : '';
            this.hiddenInput.value = fullPhone;
        }
    }
    
    validatePhone() {
        const numberInput = this.container.querySelector(`#${this.container.id}_number`);
        const isValid = this.isValidPhone();
        
        if (this.phoneNumber && !isValid) {
            numberInput.classList.add('is-invalid');
            numberInput.classList.remove('is-valid');
        } else if (this.phoneNumber && isValid) {
            numberInput.classList.add('is-valid');
            numberInput.classList.remove('is-invalid');
        } else {
            numberInput.classList.remove('is-valid', 'is-invalid');
        }
        
        return isValid;
    }
    
    isValidPhone() {
        if (!this.phoneNumber) return true; // Пустой номер разрешен
        
        // Минимальная длина номера зависит от кода страны
        const minLengths = {
            '+7': 10,      // Россия, Казахстан
            '+380': 9,     // Украина
            '+375': 9,     // Беларусь
            '+998': 9,     // Узбекистан
            '+86': 11,     // Китай
            '+1': 10,      // США/Канада
            '+44': 10,     // Великобритания
            '+49': 10,     // Германия
            '+33': 9,      // Франция
            '+39': 10,     // Италия
            '+34': 9,      // Испания
            '+81': 10,     // Япония
            '+82': 10,     // Корея
            '+91': 10,     // Индия
            '+90': 10,     // Турция
            '+971': 9,     // ОАЭ
            '+966': 9,     // Саудовская Аравия
            '+20': 10,     // Египет
            '+27': 9       // ЮАР
        };
        
        const minLength = minLengths[this.countryCode] || 7;
        return this.phoneNumber.length >= minLength;
    }
    
    getValue() {
        return this.hiddenInput ? this.hiddenInput.value : '';
    }
    
    setValue(phone) {
        if (!phone) return;
        
        // Парсим существующий номер
        const match = phone.match(/^(\+\d{1,4})(\d+)$/);
        if (match) {
            this.countryCode = match[1];
            this.phoneNumber = match[2];
            
            const countrySelect = this.container.querySelector(`#${this.container.id}_country`);
            const numberInput = this.container.querySelector(`#${this.container.id}_number`);
            
            countrySelect.value = this.countryCode;
            numberInput.value = this.phoneNumber;
            this.updateCountryDisplay();
            this.updateHiddenInput();
        }
    }
}

// Инициализация всех компонентов телефона на странице
document.addEventListener('DOMContentLoaded', function() {
    const phoneContainers = document.querySelectorAll('.phone-input');
    phoneContainers.forEach(container => {
        new PhoneInput(container.id);
    });
});
