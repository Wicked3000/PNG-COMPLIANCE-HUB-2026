document.addEventListener('DOMContentLoaded', () => initCustomSelects());
document.addEventListener('htmx:afterSwap', (e) => initCustomSelects(e.target));

function initCustomSelects(root = document) {
    root.querySelectorAll('select.form-select').forEach(select => {
        if (select.dataset.customized || select.disabled) return;
        select.dataset.customized = "true";

        const wrapper = document.createElement('div');
        wrapper.className = 'dropdown custom-select-wrapper';
        wrapper.style.position = 'relative';
        wrapper.style.width = '100%';

        select.style.display = 'none';
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);

        const btn = document.createElement('div');
        btn.className = select.className;
        btn.classList.add('text-start');
        btn.setAttribute('data-bs-toggle', 'dropdown');
        btn.setAttribute('tabindex', '0');
        btn.style.cursor = 'pointer';
        // Prevent empty height issues
        btn.style.minHeight = '42px';
        btn.style.display = 'flex';
        btn.style.alignItems = 'center';

        const menu = document.createElement('div');
        menu.className = 'dropdown-menu w-100';
        menu.style.maxHeight = '250px';
        menu.style.overflowY = 'auto';

        const updateSelection = () => {
            const selectedOption = select.options[select.selectedIndex];
            if(selectedOption) {
                btn.textContent = selectedOption.text;
                if (selectedOption.value === "") {
                    btn.style.color = 'rgba(255, 255, 255, 0.7)';
                } else {
                    btn.style.color = 'var(--text-primary)';
                }
            }
            menu.querySelectorAll('.dropdown-item').forEach(item => {
                if (item.dataset.value === select.value) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        };

        Array.from(select.options).forEach((opt, idx) => {
            const item = document.createElement('a');
            item.className = 'dropdown-item';
            item.href = '#';
            item.dataset.value = opt.value;
            item.textContent = opt.text;
            
            item.addEventListener('click', (e) => {
                e.preventDefault();
                select.selectedIndex = idx;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                updateSelection();
            });
            menu.appendChild(item);
        });

        updateSelection();
        
        wrapper.appendChild(btn);
        wrapper.appendChild(menu);
        
        select.addEventListener('change', updateSelection);
    });
}
