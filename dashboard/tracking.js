// Nessus Visitor Tracking Script
(function() {
  'use strict';

  // Configuration
  const TRACKING_ENDPOINT = 'https://rjudjhjcfivugbyztnce.supabase.co/functions/v1/track-visitor';
  const CLIENT_ID = 'e3387ba4-916b-4eeb-b042-5ed57a93fe1c'; // Ausfaller client ID

  // Generate or retrieve session ID
  function getSessionId() {
    let sessionId = sessionStorage.getItem('nessus_session_id');
    if (!sessionId) {
      sessionId = 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
      sessionStorage.setItem('nessus_session_id', sessionId);
    }
    return sessionId;
  }

  // Track page visit
  function trackVisit() {
    const data = {
      client_id: CLIENT_ID,
      page_path: window.location.pathname + window.location.search,
      referrer: document.referrer || null,
      user_agent: navigator.userAgent,
      session_id: getSessionId(),
    };

    // Use sendBeacon for reliability (won't block page unload)
    if (navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      navigator.sendBeacon(TRACKING_ENDPOINT, blob);
    } else {
      // Fallback to fetch
      fetch(TRACKING_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        keepalive: true,
      }).catch(() => {
        // Silently fail - don't impact user experience
      });
    }
  }

  // Track on page load
  if (document.readyState === 'complete') {
    trackVisit();
  } else {
    window.addEventListener('load', trackVisit);
  }

  // Expose for manual tracking if needed
  window.nessusTrack = trackVisit;
})();
