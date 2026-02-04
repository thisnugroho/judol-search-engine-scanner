<script>
    import { onMount, createEventDispatcher } from "svelte";
    import "@cap.js/widget";

    export let onVerify = undefined;

    const dispatch = createEventDispatcher();
    let widget;
    let verifying = false;

    const host = import.meta.env.VITE_CAPTCHA_HOST;
    const siteKey = import.meta.env.VITE_SITE_KEY;
    const captchaEndpoint = `${host}/${siteKey}/`;


    onMount(() => {
        if (widget) {
            const handleSolve = (e) => {
                verifying = true; // Show loading state like in the example
                const token = e.detail?.token;

                // Small delay to show the verifying state if desired, or just dispatch immediately
                setTimeout(() => {
                    dispatch("verify", { token });
                    if (onVerify) onVerify();
                }, 800);
            };

            widget.addEventListener("solve", handleSolve);

            return () => {
                if (widget) widget.removeEventListener("solve", handleSolve);
            };
        }
    });
</script>

<div class="security-card">
    {#if !verifying}
        <div class="header-spinner"></div>
        <h1>Security Verification</h1>
        <div class="subtitle">Please verify that you're human to continue</div>
        <div class="info-text">
            Complete the verification challenge below to access the requested
            content.
        </div>

        <div class="captcha-box">
            <cap-widget
                bind:this={widget}
                data-cap-api-endpoint={captchaEndpoint}
                data-cap-i18n-verifying-label="Memverifikasi..."
                data-cap-i18n-solved-label="Anda Manusia"
                data-cap-i18n-error-label="Error. Coba lagi."
                data-cap-i18n-initial-state="Saya Manusia"
            ></cap-widget>
        </div>
    {:else}
        <div class="loading">
            <div class="spinner-small"></div>
            <span>Verifying...</span>
        </div>
    {/if}

    <div class="security-info">
        <svg viewBox="0 0 24 24" fill="currentColor">
            <path
                d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z"
            />
        </svg>
        <span>Protected by Vortex Shield</span>
    </div>
</div>

<style>
    /* Adapted from captcah-example.html to match Svelte encapsulation */
    .security-card {
        background: #2d3748;
        color: #e2e8f0;
        padding: 32px;
        border-radius: 12px;
        text-align: center;
        width: 100%;
        max-width: 480px;
        font-family: "Inter", system-ui, sans-serif;
        box-shadow:
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin: 0 auto;
    }

    .header-spinner {
        width: 48px;
        height: 48px;
        border: 4px solid #f3f4f6;
        border-top: 4px solid #0d9488;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 24px;
        opacity: 0.8;
    }

    h1 {
        font-size: 24px;
        font-weight: 600;
        color: #f7fafc;
        margin-bottom: 8px;
    }

    .subtitle {
        font-size: 16px;
        color: #a0aec0;
        margin-bottom: 24px;
    }

    .info-text {
        font-size: 14px;
        color: #a0aec0;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    .captcha-box {
        background: #4a5568;
        border: 1px solid #718096;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80px;
    }

    .security-info {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-size: 12px;
        color: #9ca3af;
        margin-top: 24px;
    }

    .security-info svg {
        width: 14px;
        height: 14px;
    }

    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        color: #a0aec0;
        font-size: 14px;
        padding: 40px 0;
    }

    .spinner-small {
        width: 24px;
        height: 24px;
        border: 3px solid #f3f4f6;
        border-top: 3px solid #0d9488;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>
