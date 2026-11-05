// Form readiness test: which REQUIRED fields are still empty. Run via javascript_tool on the form tab.
// Returns {form, required, empty_count, empty:[labels], warning?}. Ready = empty_count 0, or only fields
// deliberately left to the candidate and named in the report. Tool "success" reports are not proof; this is.
// Reads the DOM: on Ashby the final proof is the Submit response; on Rippling/Gem it can be false-green.
// Required = asterisk in label (Greenhouse), "required" class on label (Ashby CSS asterisk), or
// required/aria-required attribute. react-select empties its input after a pick → also check singleValue.
// Scope = the <form> with the most fields (the first form is often the site search), else document.

(() => {
  const clean = s => (s || '').replace(/\s+/g, ' ').trim();
  const FIELDS = 'input:not([type=hidden]),textarea,select';
  const forms = [...document.querySelectorAll('form')];
  const form = forms.sort((a, b) => b.querySelectorAll(FIELDS).length - a.querySelectorAll(FIELDS).length)[0]
    || document;
  const scope = form === document ? 'document'
    : clean(form.id || form.getAttribute('name') || form.getAttribute('action') || form.className).slice(0, 60) || 'form';
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
    // A label of one radio option ("0 - 2 weeks") is not a separate required field.
    .filter(g => !g.el.htmlFor
              || !g.box.querySelector(`input[type=radio]#${CSS.escape(g.el.htmlFor)}`))
    // Lever: the option label wraps the radio itself, without htmlFor ("Yes/No/Unsure" showed as
    // empty while answered). Collapse such labels into one group per name: filled if anything in
    // the group is checked. A single checkbox (consent) stays its own field.
    .filter((g, _, all) => {
      const opt = g.el.querySelector('input[type=radio],input[type=checkbox]');
      if (!opt || form.querySelectorAll(`input[name="${CSS.escape(opt.name)}"]`).length < 2) return true;
      g.box = opt.closest('fieldset, ul, .application-question, .custom-question') || g.box.parentElement;
      const q = opt.closest('fieldset, .application-question, .custom-question');
      g.label = clean((q && q.querySelector('legend, .application-label, .text') || g.el).innerText).slice(0, 70);
      return all.find(o => o.el.querySelector(`input[name="${CSS.escape(opt.name)}"]`)) === g;
    });

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
    // Attached file = a file NAME ("Name_CV.pdf"), not the hint "Accepted: .pdf, .docx".
    if (/\w\.(pdf|docx?|txt|rtf)\b/i.test(box.textContent)) return true;
    return false;
  };

  const empty = groups.filter(g => !isFilled(g.box)).map(g => g.label);
  const out = { form: scope, required: groups.length, empty_count: empty.length, empty };
  // False green guard: fields exist but no required label was recognised (Gem, HR-Manager, custom
  // forms whose labels aren't <label>). Zero is then not proof — dump the values by JS.
  const visible = [...form.querySelectorAll(FIELDS)].filter(el => el.offsetParent !== null).length;
  if (!groups.length && visible > 2) {
    out.warning = `0 required recognised but ${visible} visible fields — labels may not be <label>; verify by JS dump`;
  }
  return out;
})()
