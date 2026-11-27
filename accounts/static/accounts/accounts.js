
document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', () => {

    const buttons = document.querySelectorAll(
        '[data-password-toggle]'
    );

    buttons.forEach(button => {

        button.addEventListener('click', () => {

            const wrapper = button.closest(
                '.acc-input-wrapper'
            );

            const input = wrapper.querySelector('input');

            if (input.type === 'password') {
                input.type = 'text';
                button.textContent = 'Сховати';
                button.setAttribute(
                    'aria-label',
                    'Сховати пароль'
                );
            } else {
                input.type = 'password';
                button.textContent = 'Показати';
                button.setAttribute(
                    'aria-label',
                    'Показати пароль'
                );
            }

        });

    });

});
