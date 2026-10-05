// Form readiness test: which REQUIRED fields are still empty. Run via javascript_tool on the form tab.
// Returns {required, empty_count, empty:[labels]}. Ready = empty_count 0, or only fields deliberately
// left to the candidate and named in the report. Tool "success" reports are not proof; this is.
// Reads the DOM: on Ashby the final proof is the Submit response; on Rippling it can be false-green.
// Required = asterisk in label (Greenhouse), "required" class on label (Ashby CSS asterisk), or
// required/aria-required attribute. react-select empties its input after a pick → also check singleValue.

(() => {
  const clean = s => (s || '').replace(/\s+/g, ' ').trim();
  const form = document.querySelector('form') || document;
  const isRequiredLabel = l =>
    /\*/.test(l.innerText) || /required/i.test(l.className || '');
  const groups = [...form.querySelectorAll('label')]
    .map(l => {
      let box = l.parentElement;
      for (let i = 0; i < 3 && box && !box.querySelector('input,textarea,select'); i++) {
        box = box.parentElement;
      }
      return { label: clean(l.innerText).slice(0, 70), box, el: l };
    })
    .filter(g => g.box)
    .filter(g => isRequiredLabel(g.el)
              || g.box.querySelector('[required],[aria-required="true"]'))
    .filter(g => !g.el.htmlFor
              || !g.box.querySelector(`input[type=radio]#${CSS.escape(g.el.htmlFor)}`));

  const isFilled = box => {
    for (const el of box.querySelectorAll('input,textarea,select')) {
      if (el.type === 'file') { if (el.files && el.files.length) return true; continue; }
      if (el.type === 'checkbox' || el.type === 'radio') { if (el.checked) return true; continue; }
      if (el.value && String(el.value).trim()) return true;
    }
    const sv = box.querySelector(
      '[class*="singleValue"],[class*="single-value"],[class*="multiValue"],[class*="multi-value"]'
    );
    if (sv && clean(sv.textContent)) return true;
    if (/\.(pdf|docx?|txt|rtf)\b/i.test(box.textContent)) return true;   // attached file
    return false;
  };

  const empty = groups.filter(g => !isFilled(g.box)).map(g => g.label);
  return { required: groups.length, empty_count: empty.length, empty };
})()
