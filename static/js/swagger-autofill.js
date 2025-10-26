// Simple helper to persist data between Swagger operations and autofill forms.
// Focus: OTP flow (copy target/purpose from request to verify form automatically).

window.SwaggerAutofill = (function(){
  const OTP_REQUEST_PATH = '/api/accounts/otp/request/';
  const OTP_VERIFY_PATH  = '/api/accounts/otp/verify/';

  function onRequest(req) {
    try {
      if ((req.url || req.pathName || '').includes(OTP_REQUEST_PATH) && req.body) {
        const body = JSON.parse(req.body);
        if (body.target)  localStorage.setItem('otp_target', String(body.target));
        if (body.purpose) localStorage.setItem('otp_purpose', String(body.purpose));
      }
    } catch(e) { /* noop */ }
  }

  function patchOTPVerifyTextareas() {
    const target = localStorage.getItem('otp_target');
    const purpose = localStorage.getItem('otp_purpose');
    if (!target && !purpose) return;

    // Find the opblock for OTP Verify
    const blocks = document.querySelectorAll('.opblock');
    blocks.forEach(block => {
      try {
        const pathEl = block.querySelector('.opblock-summary-path');
        const methodEl = block.querySelector('.opblock-summary-method');
        const pathText = (pathEl && pathEl.textContent) || '';
        const method = (methodEl && methodEl.textContent || '').toLowerCase();
        if (pathText.includes(OTP_VERIFY_PATH) && method === 'post') {
          // Ensure Try-it-out clicked: look for an editable textarea in request body
          const textarea = block.querySelector('textarea');
          if (!textarea) return;
          try {
            const json = JSON.parse(textarea.value || '{}');
            if (target && !json.target) json.target = target;
            if (purpose && !json.purpose) json.purpose = purpose;
            textarea.value = JSON.stringify(json, null, 2);
            textarea.dispatchEvent(new Event('input', {bubbles:true}));
          } catch(e) {
            // If not JSON yet, write a basic template
            const tpl = {};
            if (target) tpl.target = target;
            if (purpose) tpl.purpose = purpose;
            tpl.code = tpl.code || '';
            textarea.value = JSON.stringify(tpl, null, 2);
            textarea.dispatchEvent(new Event('input', {bubbles:true}));
          }
        }
      } catch(e) { /* noop */ }
    });
  }

  function onReady() {
    // Patch when user toggles Try it out or expands the OTP verify operation
    document.body.addEventListener('click', function(ev){
      const el = ev.target;
      if (!el) return;
      const txt = (el.textContent || '').toLowerCase();
      if (txt.includes('try it out') || txt.includes('otp') || el.matches('.opblock-summary')) {
        setTimeout(patchOTPVerifyTextareas, 200);
        setTimeout(patchOTPVerifyTextareas, 600);
      }
    }, true);

    // Also attempt initial patch shortly after load
    setTimeout(patchOTPVerifyTextareas, 800);
  }

  return { onRequest, onReady };
})();

