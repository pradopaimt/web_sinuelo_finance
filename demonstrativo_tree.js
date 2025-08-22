(() => {
  const API = (typeof window !== 'undefined' && window.API_BASE) ? window.API_BASE : '';
  const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

  const $tree = () => document.getElementById('demonstrativo_tree');
  const $err  = () => document.getElementById('err');
  const $sel  = () => document.getElementById('visaoDemonstrativos');

  let cache = null;

  // ---- helpers ----
  const esc = (s) => String(s ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');

  function currencyBRL(v) {
    const n = Number(v || 0);
    return isFinite(n)
      ? n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
      : 'R$ 0,00';
  }

  function parseAnoMes(iso) {
    if (!iso) return { ano: null, mes: null, dia: null };
    // importante: fixar TZ para não “andar” a data
    const d = new Date(String(iso) + 'T00:00:00');
    return { ano: d.getFullYear(), mes: d.getMonth(), dia: d.getDate() };
  }

  async function fetchDemonstrativos() {
    const res = await fetch(`${API}/demonstrativos`, { credentials: 'include' }).catch(() => null);
    if (!res || !res.ok) throw new Error('Falha ao carregar demonstrativos');
    return res.json();
  }

  // ---------- VISÃO 1: Safra / Ano ----------
  function buildTreeBySafraAno(data) {
    const group = {};
    for (const it of data) {
      const safra = it.safra || 'Sem safra';
      const ano = it.ano || (it.data ? parseAnoMes(it.data).ano : 's/ano');
      group[safra] ??= {};
      group[safra][ano] ??= [];
      group[safra][ano].push(it);
    }

    let html = '';
    Object.keys(group).sort().forEach(safra => {
      const anos = group[safra];
      const totalSafra = Object.values(anos).flat().reduce((s,a)=>s+(+a.valor||0),0);
      html += `<details open>
        <summary><strong>${esc(safra)}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalSafra)}</span></summary>
        <div style="margin-left:16px">`;
      Object.keys(anos).sort().forEach(ano => {
        const itens = anos[ano];
        const totalAno = itens.reduce((s,a)=>s+(+a.valor||0),0);
        html += `<details>
          <summary><strong>${esc(ano)}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalAno)}</span></summary>
          <div style="margin-left:16px">
            ${itens.map(i => {
              const dataStr = i.data ? new Date(i.data + 'T00:00:00').toLocaleDateString('pt-BR') : '';
              return `<div>• ${dataStr} — ${esc(i.descricao) || '(sem descrição)'} — <span class="value">${currencyBRL(i.valor)}</span></div>`;
            }).join('')}
          </div>
        </details>`;
      });
      html += `</div></details>`;
    });

    return html || `<div class="muted">Nenhum dado para exibir.</div>`;
  }

  // ---------- VISÃO 2: Ano / Mês ----------
  function buildTreeByAnoMes(data) {
    const group = {};
    for (const it of data) {
      const { ano, mes } = parseAnoMes(it.data);
      if (!ano && !it.ano) continue;
      const a = ano || it.ano;
      const m = (typeof mes === 'number') ? mes : -1;
      group[a] ??= {};
      group[a][m] ??= [];
      group[a][m].push(it);
    }

    let html = '';
    Object.keys(group).sort().forEach(ano => {
      const mesesObj = group[ano];
      const totalAno = Object.values(mesesObj).flat().reduce((s,a)=>s+(+a.valor||0),0);
      html += `<details open>
        <summary><strong>${esc(ano)}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalAno)}</span></summary>
        <div style="margin-left:16px">`;

      const keys = Object.keys(mesesObj).map(x=>+x).sort((a,b)=>a-b);
      for (const m of keys) {
        const itens = mesesObj[m];
        const totalMes = itens.reduce((s,a)=>s+(+a.valor||0),0);
        const rotulo = (m>=0 && m<=11) ? MESES_PT[m] : 'Sem mês';
        html += `<details>
          <summary><strong>${rotulo}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalMes)}</span></summary>
          <div style="margin-left:16px">
            ${itens.map(i => {
              const dt = i.data ? new Date(i.data + 'T00:00:00').toLocaleDateString('pt-BR') : '';
              const tagSafra = i.safra ? ` <span class="muted">[${esc(i.safra)}]</span>` : '';
              return `<div>• ${dt} — ${esc(i.descricao) || '(sem descrição)'}${tagSafra} — <span class="value">${currencyBRL(i.valor)}</span></div>`;
            }).join('')}
          </div>
        </details>`;
      }
      html += `</div></details>`;
    });

    return html || `<div class="muted">Nenhum dado para exibir.</div>`;
  }

  // ---------- Controller ----------
  async function render() {
    const tree = $tree(); const err = $err(); const sel = $sel();
    if (!tree) return;

    try {
      if (!cache) cache = await fetchDemonstrativos();
      const visao = (sel && sel.value) || 'safra';
      const html = (visao === 'mes') ? buildTreeByAnoMes(cache) : buildTreeBySafraAno(cache);
      tree.innerHTML = html;
      if (err) { err.textContent = ''; err.style.display = 'none'; }
    } catch (e) {
      if (tree) tree.innerHTML = '';
      if (err) { err.textContent = e.message || 'Erro ao carregar demonstrativos'; err.style.display = 'block'; }
      console.error(e);
    }
  }

  function bindControls() {
    const sel = $sel();
    if (sel) {
      sel.value = localStorage.getItem('visaoDemonstrativos') || 'safra';
      sel.addEventListener('change', () => {
        localStorage.setItem('visaoDemonstrativos', sel.value);
        render();
      });
    }
    const exp = document.getElementById('expandAll');
    const col = document.getElementById('collapseAll');
    if (exp) exp.onclick = () => {
      document.querySelectorAll('#demonstrativo_tree details').forEach(d => d.open = true);
    };
    if (col) col.onclick = () => {
      document.querySelectorAll('#demonstrativo_tree details').forEach(d => d.open = false);
    };
  }

  // Expor uma API para re-render (e limpar cache) quando houver mudança de dados no app
  window.DemonstrativoTree = {
    refresh: () => { cache = null; render(); }
  };

  document.addEventListener('DOMContentLoaded', () => {
    bindControls();
    render();
  });
})();
