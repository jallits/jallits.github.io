(() => {
  'use strict';

  const config = window.JALLITS_ANALYTICS || {};
  const container = config.tagManagerId || '';
  const measurement = config.measurementId || '';
  // Reject malformed IDs and ambiguous configuration rather than double-counting.
  if (container && measurement) return;
  const useTagManager = /^GTM-[A-Z0-9]+$/.test(container);
  const useAnalytics = /^G-[A-Z0-9]+$/.test(measurement);
  if ((container && !useTagManager) || (measurement && !useAnalytics)) return;
  if (!useTagManager && !useAnalytics) return;
  if (window.__jallitsAnalyticsLoaded) return;
  window.__jallitsAnalyticsLoaded = true;

  window.dataLayer = window.dataLayer || [];
  const script = document.createElement('script');
  script.async = true;
  if (useTagManager) {
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    script.src = 'https://www.googletagmanager.com/gtm.js?id=' + container;
  } else {
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', measurement);
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurement;
  }
  document.head.appendChild(script);
})();
