/**
 * Компонент кнопки "Наверх"
 */
class BackToTop {
    constructor(options = {}) {
        this.options = {
            showAfter: 300, // Показать после скролла на 300px
            animationDuration: 500, // Длительность анимации
            buttonClass: 'back-to-top-btn',
            icon: 'fas fa-arrow-up',
            ...options
        };
        
        this.button = null;
        this.isVisible = false;
        this.init();
    }
    
    init() {
        this.createButton();
        this.bindEvents();
    }
    
    createButton() {
        // Создаем кнопку
        this.button = document.createElement('button');
        this.button.className = this.options.buttonClass;
        this.button.innerHTML = `<i class="${this.options.icon}"></i>`;
        this.button.setAttribute('aria-label', 'Наверх');
        this.button.setAttribute('title', 'Наверх');
        
        // Стили кнопки
        this.button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        `;
        
        // Добавляем кнопку в body
        document.body.appendChild(this.button);
        
        // Hover эффекты
        this.button.addEventListener('mouseenter', () => {
            this.button.style.transform = 'scale(1.1)';
            this.button.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.4)';
        });
        
        this.button.addEventListener('mouseleave', () => {
            this.button.style.transform = 'scale(1)';
            this.button.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
        });
    }
    
    bindEvents() {
        // Обработчик скролла
        window.addEventListener('scroll', () => this.handleScroll());
        
        // Обработчик клика
        this.button.addEventListener('click', () => this.scrollToTop());
    }
    
    handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > this.options.showAfter) {
            this.show();
        } else {
            this.hide();
        }
    }
    
    show() {
        if (!this.isVisible) {
            this.isVisible = true;
            this.button.style.opacity = '1';
            this.button.style.visibility = 'visible';
        }
    }
    
    hide() {
        if (this.isVisible) {
            this.isVisible = false;
            this.button.style.opacity = '0';
            this.button.style.visibility = 'hidden';
        }
    }
    
    scrollToTop() {
        // Плавная прокрутка наверх
        const startPosition = window.pageYOffset;
        const startTime = performance.now();
        
        const animateScroll = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / this.options.animationDuration, 1);
            
            // Easing функция для плавности
            const easeInOutCubic = progress < 0.5 
                ? 4 * progress * progress * progress 
                : 1 - Math.pow(-2 * progress + 2, 3) / 2;
            
            window.scrollTo(0, startPosition * (1 - easeInOutCubic));
            
            if (progress < 1) {
                requestAnimationFrame(animateScroll);
            }
        };
        
        requestAnimationFrame(animateScroll);
    }
}

// Автоматическая инициализация
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем только на главной странице
    const isHomePage = window.location.pathname === '/' || 
                      window.location.pathname === '/index/' ||
                      document.body.classList.contains('home-page');
    
    if (isHomePage) {
        new BackToTop();
    }
});

// Функция для ручной инициализации
function initBackToTop(options = {}) {
    return new BackToTop(options);
}
