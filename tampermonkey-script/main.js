// ==UserScript==
// @name         Cursor Reset Trial
// @namespace    http://tampermonkey.net/
// @version      1.0.1
// @description  Reset Cursor Trial - Reset their Cursor trial period
// @author       ovftank
// @homepage     https://github.com/ovftank/cursor-reset-trial/tree/main/tampermonkey-script
// @supportURL   https://github.com/ovftank
// @match        https://www.cursor.com/*
// @match        https://authenticator.cursor.sh/*
// @grant        GM_xmlhttpRequest
// @icon         https://github.com/ovftank/cursor-reset-trial/raw/refs/heads/main/images/icon.ico
// @updateURL    https://raw.githubusercontent.com/ovftank/cursor-reset-trial/refs/heads/main/tampermonkey-script/main.js
// @downloadURL  https://raw.githubusercontent.com/ovftank/cursor-reset-trial/refs/heads/main/tampermonkey-script/main.js
// @contactURL   https://t.me/ovftank
// @copyright    2024, ovftank (https://greasyfork.org/users/1392240-ovftank)
// ==/UserScript==

(() => {
    'use strict';

    const createToastStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes toastFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .toast-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 99999;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .toast-container {
                background-color: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 20px;
                border-radius: 8px;
                min-width: 300px;
                text-align: center;
                animation: toastFadeIn 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .toast-message {
                margin-bottom: 16px;
                font-size: 16px;
            }

            .toast-buttons {
                display: flex;
                justify-content: center;
                gap: 8px;
            }

            .toast-button {
                padding: 8px 16px;
                border-radius: 12px;
                color: white;
                cursor: pointer;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }

            .toast-button:hover {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }

            .confirm-button {
                background-color: white;
                color: black;
                border: none;
            }

            .confirm-button:hover {
                background-color: #f0f0f0;
            }

            .cancel-button {
                background-color: #666;
            }

            .cancel-button:hover {
                background-color: #777;
            }

            .delete-account-button {
                width: 100%;
                margin-top: 8px;
                padding: 8px 16px;
                background-color: #1a1a1a;
                border: 1px solid white;
                color: white;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .delete-account-button:hover {
                background-color: #2a2a2a;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }

            .loading-spinner {
                width: 24px;
                height: 24px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s linear infinite;
                margin: 0 auto;
                display: none;
            }

            @keyframes spin {
                to {
                    transform: rotate(360deg);
                }
            }

            .toast-message.loading .loading-spinner {
                display: block;
                margin-top: 12px;
            }
        `;
        document.head.appendChild(style);
    };

    const showConfirmToast = (message, onConfirm, autoConfirm = false) => {
        const overlay = document.createElement('div');
        overlay.className = 'toast-overlay';

        const toast = document.createElement('div');
        toast.className = 'toast-container';
        toast.innerHTML = `
            <div class="toast-message">${message}
                <div class="loading-spinner"></div>
            </div>
            <div class="toast-buttons">
                <button class="toast-button confirm-button">Confirm</button>
                <button class="toast-button cancel-button">Cancel</button>
            </div>
        `;

        const confirmBtn = toast.querySelector('.confirm-button');
        const cancelBtn = toast.querySelector('.cancel-button');
        const messageDiv = toast.querySelector('.toast-message');
        const buttons = toast.querySelector('.toast-buttons');

        const confirmAction = () => {
            messageDiv.classList.add('loading');
            buttons.style.display = 'none';
            messageDiv.textContent = 'Processing...';
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            messageDiv.appendChild(spinner);
            onConfirm(overlay);
        };

        if (autoConfirm) {
            setTimeout(confirmAction, 500);
        } else {
            confirmBtn.addEventListener('click', confirmAction);
            cancelBtn.addEventListener('click', () => {
                document.body.removeChild(overlay);
            });
        }

        overlay.appendChild(toast);
        document.body.appendChild(overlay);
    };

    const waitForElement = (selector, callback, maxAttempts = 10) => {
        let attempts = 0;

        const checkElement = () => {
            attempts++;
            const element = document.querySelector(selector);

            if (element) {
                callback(element);
                return;
            }

            if (attempts < maxAttempts) {
                setTimeout(checkElement, 1000);
            } else {
                console.log('Không tìm thấy phần tử sau nhiều lần thử');
            }
        };

        checkElement();
    };

    const resetTrial = (overlay) => {
        sendCallback({ action: 'reset_loading' });

        GM_xmlhttpRequest({
            method: 'POST',
            url: 'https://www.cursor.com/api/dashboard/delete-account',
            headers: {
                'Content-Type': 'application/json'
            },
            onload: (response) => {
                if (response.status === 200) {
                    sendCallback({ action: 'reset_complete' });
                    document.body.removeChild(overlay);
                    window.location.href = 'https://authenticator.cursor.sh';
                } else {
                    sendCallback({
                        action: 'reset_failed',
                        error: 'Server returned status ' + response.status
                    });
                    const messageDiv = overlay.querySelector('.toast-message');
                    const buttons = overlay.querySelector('.toast-buttons');
                    messageDiv.classList.remove('loading');
                    messageDiv.textContent = 'Failed to reset trial. Please try again.';
                    buttons.style.display = 'flex';
                }
            },
            onerror: (error) => {
                console.error('Error:', error);
                sendCallback({
                    action: 'reset_failed',
                    error: error.toString()
                });
                const messageDiv = overlay.querySelector('.toast-message');
                const buttons = overlay.querySelector('.toast-buttons');
                messageDiv.classList.remove('loading');
                messageDiv.textContent = 'An error occurred. Please try again.';
                buttons.style.display = 'flex';
            }
        });
    };

    const handleAutomation = () => {
        const currentURL = window.location.href;

        if (currentURL === 'https://www.cursor.com/') {
            window.location.href = 'https://www.cursor.com/settings';
        }
        else if (currentURL.startsWith('https://authenticator.cursor.sh/')) {
            waitForElement("body > div.radix-themes > div > div > div:nth-child(2) > div > form > div > div.rt-Grid.rt-r-gap-3 > a:nth-child(2)",
                (element) => {
                    element.click();
                }
            );
        }
    };

    const initialize = () => {
        createToastStyles();

        handleAutomation();

        if (window.location.href.startsWith('https://www.cursor.com/settings')) {
            const urlParams = new URLSearchParams(window.location.search);
            const shouldAutoReset = urlParams.get('reset') === 'true';

            const targetSelector = 'body > main > div > div > div > div > div > div.col-span-1.flex.flex-col.gap-2.xl\\:gap-4 > div:nth-child(1)';
            waitForElement(targetSelector, (targetDiv) => {
                const button = document.createElement('button');
                button.innerHTML = 'Reset Trial';
                button.className = 'delete-account-button';

                button.addEventListener('click', () => {
                    showConfirmToast('Are you sure you want to reset your trial?', resetTrial);
                });
                targetDiv.appendChild(button);

                if (shouldAutoReset) {
                    showConfirmToast('Are you sure you want to reset your trial?', resetTrial, true);
                }
            });
        }
    };

    // Function to send callback to local application
    async function sendCallback(data) {
        try {
            const response = await fetch('http://localhost:8765', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error sending callback:', error);
        }
    }

    initialize();
})();
