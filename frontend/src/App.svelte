<script>
  import { onMount } from "svelte";
  import { fly, fade, slide } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  let domain = "";
  let results = [];
  let loading = false;
  let error = "";
  let hasAttempted = false;
  let searched = false;
  let verified = false;
  let searchedDomain = "";
  let captchaToken = null;

  const enableCaptcha = import.meta.env.VITE_ENABLE_CAPTCHA !== "false";
  const recaptchaSiteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY;
  const keywordHighlightRegex = /(gacor|slot777|slot888|casino|poker|togel|maxwin|zeus)/gi;
  const keywordTestRegex = /(gacor|slot777|slot888|casino|poker|togel|maxwin|zeus)/i;
  const contactHref = "mailto:contact@genbucyber.com";
  const contactLabel = "Kirim Email";
  let recaptchaReady = false;
  let recaptchaWidgetId = null;
  let showCtaModal = false;
  let shouldShowCta = false;
  let hasShownCta = false;
  let hasScrolled = false;

  function isAtPageBottom() {
    const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
    const viewport = window.innerHeight || document.documentElement.clientHeight || 0;
    const fullHeight = document.documentElement.scrollHeight || document.body.scrollHeight || 0;
    return scrollY + viewport >= fullHeight - 2;
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Gagal memuat ${src}`));
      document.head.appendChild(script);
    });
  }

  async function loadRecaptchaScript() {
    if (window.grecaptcha && typeof window.grecaptcha.render === "function") {
      recaptchaReady = true;
      return;
    }

    window.__recaptchaOnload = () => {
      recaptchaReady = true;
      renderRecaptcha();
    };

    const params = "onload=__recaptchaOnload&render=explicit";
    try {
      await loadScript(`https://www.google.com/recaptcha/api.js?${params}`);
    } catch (err) {
      await loadScript(`https://www.recaptcha.net/recaptcha/api.js?${params}`);
    }
  }

  function renderRecaptcha() {
    if (!window.grecaptcha || typeof window.grecaptcha.render !== "function" || !recaptchaSiteKey) return;
    if (recaptchaWidgetId !== null) return;

    recaptchaWidgetId = window.grecaptcha.render("recaptcha-container", {
      sitekey: recaptchaSiteKey,
      callback: (token) => {
        captchaToken = token;
        verified = true;
      },
      "expired-callback": () => {
        captchaToken = null;
        verified = false;
      },
      "error-callback": () => {
        captchaToken = null;
        verified = false;
      },
    });
  }

  onMount(async () => {
    if (!enableCaptcha) return;

    if (!recaptchaSiteKey) {
      error = "reCAPTCHA site key belum diset.";
      return;
    }

    try {
      await loadRecaptchaScript();
      renderRecaptcha();
      recaptchaReady = true;
    } catch (err) {
      console.error(err);
      error = "Gagal memuat reCAPTCHA. Coba refresh halaman.";
    }
  });

  onMount(() => {
    const onScroll = () => {
      const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
      if (scrollY > 0) {
        hasScrolled = true;
      }
      if (!shouldShowCta || hasShownCta || loading || error) return;
      if (hasScrolled && isAtPageBottom()) {
        showCtaModal = true;
        hasShownCta = true;
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  });

  function initiateSearch() {
    if (!domain.trim()) {
      error = "Tulis domain yang mau dicek dulu.";
      hasAttempted = true;
      return;
    }

    error = "";
    hasAttempted = true;

    if ((verified && captchaToken) || !enableCaptcha) {
      const token = !enableCaptcha && !captchaToken ? "CAPTCHA_DISABLED" : captchaToken;
      captchaToken = token;
      handleSearch();
    } else {
      error = "Verifikasi reCAPTCHA diperlukan sebelum memindai.";
    }
  }

  async function handleSearch() {
    if (!domain.trim()) {
      error = "Tulis domain yang mau dicek dulu.";
      hasAttempted = true;
      return;
    }

    if (enableCaptcha && !captchaToken) {
      error = "Verifikasi reCAPTCHA diperlukan sebelum memindai.";
      hasAttempted = true;
      return;
    }

    loading = true;
    error = "";
    results = [];
    searched = true;
    searchedDomain = domain;
    shouldShowCta = false;
    hasShownCta = false;
    showCtaModal = false;
    hasScrolled = false;

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: domain.trim(),
          captchaToken: captchaToken,
        }),
      });

      const text = await response.text();
      if (!text) throw new Error("Respon kosong dari server.");

      const data = JSON.parse(text);

      if (!response.ok) {
        throw new Error(data.error || "Pemindaian gagal.");
      }

      results = (data.results || []).filter((item) =>
        keywordTestRegex.test(item?.snippet || "")
      );
      if (results.length > 0) {
        shouldShowCta = true;
      } else {
        showCtaModal = false;
        shouldShowCta = false;
      }
    } catch (err) {
      console.error(err);
      error = err.message || "Koneksi gagal. Pastikan backend berjalan.";
      hasAttempted = true;
    } finally {
      loading = false;
    }
  }

  const tips = [
    "Periksa halaman yang tampil di hasil pencarian dulu.",
    "Cari pola halaman yang otomatis dibuat.",
    "Amankan akses admin dan ganti kredensial.",
  ];
</script>

<div class="min-h-screen bg-surface text-ink font-sans selection:bg-lime-200/60 selection:text-ink overflow-x-hidden">
  <div class="relative">
    <div class="hero-glow -z-10"></div>
    <div class="grain -z-10"></div>

    <div class="relative mx-auto max-w-6xl px-6 pt-12 pb-16 md:pt-16 md:pb-24">
      <header class="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] items-center">
        <div>
          <h1 class="mt-5 text-4xl font-semibold leading-tight text-ink md:text-5xl">
            Lindungi reputasi domain kamu
            <span class="text-ink/70">dari konten judol yang menempel di hasil pencarian.</span>
          </h1>
          <p class="mt-4 max-w-xl text-base text-ink/70">
            Masukkan domain untuk memindai hasil pencarian dan menemukan jejak konten mencurigakan.
            Tampilkan indikasi yang relevan, bantu cek dampak, dan beri gambaran langkah awal yang bisa diambil.
            Tetap ringkas, tetap jelas, supaya keputusan bisa dibuat lebih cepat.
          </p>
          
        </div>

        <div class="glass-card" in:fly={{ y: 12, duration: 600 }}>
          <h2 class="text-lg font-semibold text-ink">Mulai Pengecekan</h2>
          <p class="mt-2 text-sm text-ink/60">
            Pakai format domain tanpa protokol. Contoh: `example.com`.
          </p>

          <form on:submit|preventDefault={initiateSearch} class="mt-5 grid gap-3">
            {#if error && hasAttempted}
              <div class="alert" in:slide>
                <strong>Oops, pemindaian gagal.</strong>
                <span>{error}</span>
              </div>
            {/if}

            <label class="text-xs font-semibold text-ink/60">Nama domain</label>
            <div class="relative">
              <input
                type="text"
                class="input"
                placeholder="contoh: domainkamu.com"
                bind:value={domain}
                required
                aria-label="Domain"
              />
              <span class="input-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M21 21l-4.35-4.35m1.1-4.65a6.5 6.5 0 11-13 0 6.5 6.5 0 0113 0z"
                    fill="none"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-width="2"
                  />
                </svg>
              </span>
            </div>

            <button class="primary-btn" type="submit" disabled={loading}>
              {#if loading}
                <span class="spinner" aria-hidden="true"></span>
                Memindai...
              {:else}
                Mulai Scan Sekarang
              {/if}
            </button>

            {#if enableCaptcha}
              <div class="mt-3">
                <div id="recaptcha-container" class:opacity-50={!recaptchaReady}></div>
                {#if !recaptchaReady}
                  <p class="mt-2 text-xs text-ink/60">Memuat reCAPTCHA…</p>
                {/if}
              </div>
            {/if}

          </form>

          <div class="mt-6 rounded-2xl border border-ink/10 bg-white/80 p-4 text-sm text-ink/70">
            <div class="font-semibold text-ink">Langkah cepat setelah temuan</div>
            <ul class="mt-2 grid gap-2">
              {#each tips as tip}
                <li class="flex items-start gap-2">
                  <span class="dot"></span>
                  <span>{tip}</span>
                </li>
              {/each}
            </ul>
          </div>
        </div>
      </header>

      {#if showCtaModal && searched && !loading && !error && results.length > 0}
        <div class="modal">
          <div class="modal-card cta-modal" in:slide={{ duration: 260 }}>
            <div class="cta-modal-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  d="M12 3l8 4v6c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7l8-4z"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-width="2"
                />
              </svg>
            </div>
            <div class="cta-modal-body">
              <h3 class="cta-modal-title">Butuh bantuan pengamanan?</h3>
              <p class="cta-modal-copy">
                Hasil scan terindikasi konten judol. Audit dan pembersihan cepat membantu menurunkan risiko lanjutan.
              </p>
              <p class="cta-modal-note">
                Catatan: tetap lakukan verifikasi manual. Sebagian temuan bisa saja false positive.
              </p>
              <div class="cta-modal-actions">
                <button class="cta-cancel" on:click={() => (showCtaModal = false)}>Nanti dulu</button>
                <a class="cta-primary" href={contactHref}>
                  <span class="cta-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M4 6h16v12H4zM4 7l8 6 8-6"
                        fill="none"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-width="2"
                      />
                    </svg>
                  </span>
                  {contactLabel}
                </a>
              </div>
            </div>
          </div>
        </div>
      {/if}

      {#if searched && !loading && !error}
        <section class="mt-14" in:fade={{ delay: 100 }}>
          <div class="mb-6 rounded-2xl border border-slate-300/80 bg-slate-100/80 px-4 py-3 text-sm text-slate-800">
            <strong>Catatan:</strong>
            <span class="block text-slate-700">
              Hasil ini masih perlu verifikasi manual. Sebagian temuan bisa saja false positive.
            </span>
          </div>

          {#if results.length > 0}
            <div class="mb-6 rounded-2xl border border-rose-500/30 bg-rose-100/70 px-4 py-3 text-sm text-rose-900">
              <strong>Domain terindikasi kontaminasi keyword.</strong>
              <span class="block text-rose-900/80">
                Ditemukan {results.length} hasil yang memuat keyword mencurigakan.
              </span>
            </div>
            <div class="mb-6 rounded-2xl bg-emerald-600 text-white px-4 py-3 text-sm">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div class="flex items-center gap-3">
                  <span class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        fill="none"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-width="2"
                      />
                    </svg>
                  </span>
                  <div>
                    <strong>Butuh bantuan cepat?</strong>
                    <div class="text-white/85">
                      Tim security siap audit, bersihkan konten, dan bantu pemulihan reputasi domain.
                    </div>
                  </div>
                </div>
                <a class="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-xs font-semibold text-emerald-700" href={contactHref}>
                  <span class="inline-flex h-4 w-4 items-center justify-center">
                    <svg viewBox="0 0 24 24" class="h-4 w-4">
                      <path
                        d="M4 6h16v12H4zM4 7l8 6 8-6"
                        fill="none"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-width="2"
                      />
                    </svg>
                  </span>
                  {contactLabel}
                </a>
              </div>
            </div>
          {:else}
            <div class="mb-6 rounded-2xl border border-emerald-500/30 bg-emerald-100/70 px-4 py-3 text-sm text-emerald-900">
              <strong>Domain bersih dari keyword.</strong>
              <span class="block text-emerald-900/80">
                Tidak ada hasil yang memuat keyword mencurigakan.
              </span>
            </div>
          {/if}

          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 class="text-xl font-semibold text-ink">Ringkasan Hasil</h3>
              <p class="text-sm text-ink/60">
                Domain yang dicek: <span class="font-mono text-ink">{searchedDomain}</span>
              </p>
            </div>
            <div class="summary-chip">
              <span class="text-ink/60">Total temuan</span>
              <strong>{results.length}</strong>
            </div>
          </div>

          {#if results.length > 0}
            <div class="mt-6 grid gap-4">
              {#each results as result, i}
                <article
                  class="result-card"
                  in:fly={{ y: 20, delay: i * 80, duration: 650, easing: cubicOut }}
                >
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <h4 class="text-lg font-semibold text-ink line-clamp-1">{result.title}</h4>
                      <a
                        href={result.link}
                        target="_blank"
                        class="link"
                        rel="noreferrer"
                      >
                        {result.link}
                      </a>
                    </div>
                    <span class="badge">#{i + 1}</span>
                  </div>
                  <p class="mt-3 text-sm leading-relaxed text-ink/70">
                    {@html result.snippet.replace(
                      keywordHighlightRegex,
                      '<span class="highlight">$1</span>'
                    )}
                  </p>
                </article>
              {/each}
            </div>
          {:else}
            <div class="empty" in:fly={{ y: 12, duration: 500 }}>
              <div class="empty-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    fill="none"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-width="2"
                  />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-ink">Tidak ada jejak judol</h3>
              <p class="text-sm text-ink/60">
                Hasil pencarian untuk domain ini bersih dari kata kunci judol.
              </p>
            </div>
          {/if}
        </section>
      {/if}

      <footer class="mt-20 border-t border-ink/10 pt-8 text-sm text-ink/50">
        &copy; {new Date().getFullYear()} GenbuCyber. Pemindaian cepat, ringkasan jelas.
      </footer>
    </div>
  </div>
</div>
