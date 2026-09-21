"""Browser-side form field crawler for PurchaseForm.aspx."""

FORM_FIELD_EXTRACT = """() => {
  function fieldMeta(el) {
    const tag = el.tagName.toLowerCase();
    const label = (() => {
      if (el.id) {
        const l = document.querySelector('label[for="' + el.id + '"]');
        if (l) return l.innerText.trim();
      }
      const parent = el.closest('.form-group, .row, td, th, .input-group');
      if (parent) {
        const lab = parent.querySelector('label');
        if (lab && lab !== el) return lab.innerText.trim();
      }
      const prev = el.previousElementSibling;
      if (prev && prev.tagName === 'LABEL') return prev.innerText.trim();
      return el.placeholder || '';
    })();
    const opts = tag === 'select'
      ? [...el.options].map(o => ({
          value: o.value,
          text: o.text.trim(),
          selected: o.selected,
          disabled: o.disabled,
        }))
      : undefined;
    return {
      tag,
      type: el.type || null,
      id: el.id || null,
      name: el.name || null,
      label,
      placeholder: el.placeholder || null,
      value: tag === 'select' ? el.value : (el.value ?? null),
      required: el.required || el.getAttribute('aria-required') === 'true',
      disabled: el.disabled,
      maxLength: el.maxLength > 0 ? el.maxLength : null,
      options: opts,
      classes: el.className || null,
      visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length),
    };
  }

  const fields = [];
  document.querySelectorAll('input, select, textarea, button').forEach((el) => {
    const tag = el.tagName.toLowerCase();
    if (el.type === 'hidden') {
      fields.push({ ...fieldMeta(el), hidden: true });
      return;
    }
    if (tag === 'button') {
      fields.push({
        tag: 'button',
        type: el.type,
        id: el.id || null,
        label: el.innerText.trim(),
        visible: !!(el.offsetWidth || el.offsetHeight),
      });
      return;
    }
    fields.push(fieldMeta(el));
  });

  return {
    url: location.href,
    title: document.title,
    fields,
  };
}"""
