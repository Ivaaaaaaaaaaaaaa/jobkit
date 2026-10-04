// Тест готовности формы: какие ОБЯЗАТЕЛЬНЫЕ поля ещё пусты.
//
// Зачем. Отчёт браузерного инструмента — не доказательство: form_input на react-select
// отвечает «успех» и не сохраняет значение, загрузка файла может «пройти» в несуществующее
// поле. Доказательство — этот прогон.
//
// Как гонять: javascript_tool на вкладке с формой, вставив тело файла целиком.
// Возвращает {required, empty_count, empty:[...]}.
// Форма готова, только когда empty пуст или содержит ровно те поля, которые сознательно
// оставлены человеку, — и каждое названо в отчёте.
//
// Граница теста: он читает DOM. На Ashby этого мало (значение может не дойти до состояния
// формы) — там окончательная проверка — ответ формы на Submit; на Rippling тест даёт ложный
// зелёный. Подробно — playbooks/forms.md.
//
// Обязательное поле опознаётся тремя способами: звёздочка в подписи (Greenhouse), класс
// с «required» на подписи (Ashby рисует звёздочку через CSS), атрибут required/aria-required.
// У react-select видимый input после выбора пустеет — поэтому смотрим ещё singleValue
// и имя приложенного файла.

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
    if (/\.(pdf|docx?|txt|rtf)\b/i.test(box.textContent)) return true;   // приложенный файл
    return false;
  };

  const empty = groups.filter(g => !isFilled(g.box)).map(g => g.label);
  return { required: groups.length, empty_count: empty.length, empty };
})()
