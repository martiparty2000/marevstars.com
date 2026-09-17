(() => {
  const root = document.querySelector('.support-widget');
  if (!root) return;
  const panel = root.querySelector('.support-panel'), launcher = root.querySelector('.support-launcher');
  const list = root.querySelector('.support-messages'), form = root.querySelector('.support-form');
  const input = form.querySelector('textarea'), escalate = root.querySelector('.support-escalate');
  const placeholder = '00000000-0000-0000-0000-000000000000';
  let ticket = localStorage.getItem('marev_support_ticket');
  const csrf = () => document.cookie.split('; ').find(x => x.startsWith('csrftoken='))?.split('=')[1] || '';
  const thread = (end = '') => root.dataset.threadUrl.replace(placeholder, ticket) + end;
  const api = (url, options = {}) => fetch(url, { ...options, headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()} }).then(async r => { const d = await r.json(); if (!r.ok) throw Error(d.error); return d; });
  const render = rows => { list.innerHTML = ''; rows.forEach(row => { const el = document.createElement('article'); el.className = `support-message support-message-${row.author}`; el.innerHTML = `<strong>${row.author === 'visitor' ? 'Вие' : row.author === 'staff' ? 'Консултант' : 'Support'}</strong><p></p><small>${row.created_at}</small>`; el.querySelector('p').textContent = row.text; list.append(el); }); list.scrollTop = list.scrollHeight; };
  const open = () => { panel.hidden = false; launcher.setAttribute('aria-expanded', 'true'); input.focus(); if (ticket) api(thread()).then(d => { render(d.messages); escalate.hidden = d.escalated; }).catch(() => localStorage.removeItem('marev_support_ticket')); };
  const close = () => { panel.hidden = true; launcher.setAttribute('aria-expanded', 'false'); };
  launcher.onclick = open; root.querySelector('.support-close').onclick = close;
  document.querySelectorAll('.support-open').forEach(el => el.onclick = open);
  form.onsubmit = async event => { event.preventDefault(); const text = input.value.trim(); if (!text) return; input.disabled = true; try { const data = ticket ? await api(thread('message/'), {method: 'POST', body: JSON.stringify({text})}) : await api(root.dataset.startUrl, {method: 'POST', body: JSON.stringify({text})}); if (!ticket) { ticket = data.ticket; localStorage.setItem('marev_support_ticket', ticket); } render(data.messages); input.value = ''; escalate.hidden = false; } catch (error) { alert(error.message || 'Възникна проблем.'); } input.disabled = false; input.focus(); };
  escalate.onclick = async () => { try { const data = await api(thread('escalate/'), {method: 'POST', body: '{}'}); render(data.messages); escalate.hidden = true; } catch (error) { alert(error.message || 'Възникна проблем.'); } };
})();
