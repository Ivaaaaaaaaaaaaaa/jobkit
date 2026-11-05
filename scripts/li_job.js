// LinkedIn Jobs: read one vacancy from the right-hand panel of the job search page.
//
// Why: linkedin.com/jobs/view/<id> comes back without the description after ~40 views per session.
// The same job opened as linkedin.com/jobs/search/?currentJobId=<id> still shows the full text in
// the right panel. So open LinkedIn jobs only via currentJobId, never /jobs/view.
//
// How: navigate to https://www.linkedin.com/jobs/search/?currentJobId=<id>, then paste this file
// into javascript_tool (`jk lijob` prints it). Waits for the panel up to 25 s.
// Returns {id, company, title, meta, apply, applyUrl, jd}. apply: easy | external | applied | ""
// (no button = closed). External apply in the panel is a button without a URL: clicking it opens
// the ATS in a new tab, take the address from there. Empty jd = the limit reached the panel too:
// read the JD on the company ATS. This reads one page the candidate's browser already shows;
// it is not a crawler — open jobs one by one at a human pace.
(async () => {
  const pane = () => document.querySelector(
    '.jobs-search__job-details--container, .jobs-details, .scaffold-layout__detail');
  const ABOUT = /About the job|Об этой вакансии|Info zum Job|À propos de l’offre|Acerca del empleo|Informazioni sull’offerta/;
  const LOADING = /Loading job details|Загрузка сведений/;
  // A placeholder hangs under the title first — wait for the text itself.
  const ready = () => {
    const s = (pane() && pane().innerText) || '';
    const k = s.search(ABOUT);
    return k >= 0 && !LOADING.test(s) && s.length - k > 200;
  };
  // After many views the panel takes 10–15 s (spinner) but arrives — wait up to 25 s.
  for (let i = 0; i < 50 && !ready(); i++) await new Promise(r => setTimeout(r, 500));
  const p = pane();
  const t = p ? p.innerText : '';
  const lines = t.split('\n').map(s => s.trim()).filter(Boolean);
  const a = [...(p || document).querySelectorAll('a[href]')]
    .find(x => /safety\/go|externalApply/.test(x.href));
  let applyUrl = '';
  if (a) {
    try {
      const u = new URL(a.href);
      const x = new URL(u.searchParams.get('url') || a.href);
      applyUrl = x.origin + x.pathname;
    } catch (e) { /* keep empty */ }
  }
  const i = t.search(ABOUT);
  return {
    id: new URL(location.href).searchParams.get('currentJobId'),
    company: lines[0] || '',
    title: lines.find((s, k) => k > 0 && !/Share|Show more|Поделиться|Показать еще/.test(s)) || '',
    meta: lines.find(s => /·/.test(s)) || '',
    apply: /Easy Apply|Простая подача заявки/.test(t) ? 'easy'
      : /Applied \d|Заявка подана|Заявка отправлена/.test(t) ? 'applied'
      : /^(Apply|Подать заявку)$/m.test(t) ? 'external' : '',
    applyUrl,
    jd: i < 0 ? '' : t.slice(i).replace(ABOUT, '').trim().slice(0, 12000),
  };
})()
