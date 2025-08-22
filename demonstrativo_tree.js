(() => {
  const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

  const $tree = () => document.getElementById('demonstrativo_tree');
  const $err  = () => document.getElementById('err');
  const $sel  = () => document.getElementById('visaoDemonstrativos');

  function currencyBRL(v){
    const n = Number(v || 0);
    try { return n.toLocaleString('pt-BR', { style:'currency', currency:'BRL' }); }
    catch { return `R$ ${n.toFixed(2)}`; }
  }
  function safeDateParts(iso){
    if(!iso) return { ano:null, mes:null, dia:null };
    // Força meia-noite local pra evitar “virada” de fuso afetar o mês
    const d = new Date(String(iso).slice(0,10) + 'T00:00:00');
    return { ano: d.getFullYear(), mes: d.getMonth(), dia: d.getDate() };
  }

  function getData(){
    try {
      const prov = window.DemonstrativoDataProvider;
      const raw = prov?.getData?.();
      return Array.isArray(raw) ? raw : [];
    } catch { return []; }
  }

  // ============= Visão: Safra / Ano =============
  function buildTreeBySafraAno(data){
    const group = {};
    for(const it of data){
      const safra = it.safra || 'Sem safra';
      const ano = it.ano || safeDateParts(it.data).ano || 's/ano';
      (group[safra] ??= {})[ano] ??= [];
      group[safra][ano].push(it);
    }

    let html = '';
    for(const safra of Object.keys(group).sort()){
      const anos = group[safra];
      const totalSafra = Object.values(anos).flat().reduce((s,a)=> s + (+a.valor||0), 0);

      html += `<details open>
        <summary><strong>${safra}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalSafra)}</span></summary>
        <div style="margin-left:16px">`;

      for(const ano of Object.keys(anos).sort()){
        const itens = anos[ano];
        const totalAno = itens.reduce((s,a)=> s + (+a.valor||0), 0);

        html += `<details>
          <summary><strong>${ano}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalAno)}</span></summary>
          <div style="margin-left:16px">
            ${itens.map(i => {
              const dt = i.data ? new Date(i.data + 'T00:00:00').toLocaleDateString('pt-BR') : '';
              const desc = i.descricao || '(sem descrição)';
              return `<div>• ${dt} — ${desc} — <span class="value">${currencyBRL(i.valor)}</span></div>`;
            }).join('')}
          </div>
        </details>`;
      }

      html += `</div></details>`;
    }

    return html || `<div class="muted">Nenhum dado para exibir.</div>`;
  }

  // ============= Visão: Ano / Mês =============
  function buildTreeByAnoMes(data){
    const group = {};
    for(const it of data){
      const parts = safeDateParts(it.data);
      const ano = it.ano || parts.ano;
      if(!ano) continue;
      const mes = (typeof parts.mes === 'number') ? parts.mes : -1;
      (group[ano] ??= {})[mes] ??= [];
      group[ano][mes].push(it);
    }

    let html = '';
    for(const ano of Object.keys(group).map(Number).sort((a,b)=> a-b)){
      const mesesObj = group[ano];
      const totalAno = Object.values(mesesObj).flat().reduce((s,a)=> s + (+a.valor||0), 0);

      html += `<details open>
        <summary><strong>${ano}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalAno)}</span></summary>
        <div style="margin-left:16px">`;

      for(const m of Object.keys(mesesObj).map(Number).sort((a,b)=> a-b)){
        const itens = mesesObj[m];
        const totalMes = itens.reduce((s,a)=> s + (+a.valor||0), 0);
        const rotulo = (m>=0 && m<=11) ? MESES_PT[m] : 'Sem mês';

        html += `<details>
          <summary><strong>${rotulo}</strong> <span class="muted">— total</span> <span class="value">${currencyBRL(totalMes)}</span></summary>
          <div style="margin-left:16px">
            ${itens.map(i => {
              const dt = i.data ? new Date(i.data + 'T00:00:00').toLocaleDateString('pt-BR') : '';
              const desc = i.descricao || '(sem descrição)';
              const tagSafra = i.safra ? ` <span class="muted">[${i.safra}]</span>` : '';
              return `<div>• ${dt} — ${desc}${tagSafra} — <span class="value">${currencyBRL(i.valor)}</span></div>`;
            }).join('')}
          </div>
        </details>`;
      }

      html += `</div></details>`;
    }

    return html || `<div class="muted">Nenhum dado para exibir.</div>`;
  }

  // ============= Controller / Render =============
  function render(){
    const tree = $tree(); const err = $err(); const sel = $sel();
    if(!tree) return;
    try{
      const data = getData();
      const visao = (sel && sel.value) || 'safra';
      const html = (visao === 'mes') ? buildTreeByAnoMes(data) : buildTreeBySafraAno(data);
      tree.innerHTML = html;
      if(err) err.textContent = '';
    }catch(e){
      tree.innerHTML = '';
      if(err) err.textContent = e?.message || 'Erro ao montar demonstrativo';
      console.error(e);
    }
  }

  function bindControls(){
    const sel = $sel();
    if(sel){
      sel.value = localStorage.getItem('visaoDemonstrativos') || 'safra';
      sel.addEventListener('change', () => {
        localStorage.setItem('visaoDemonstrativos', sel.value);
        render();
      });
    }
    const exp = document.getElementById('expandAll');
    const col = document.getElementById('collapseAll');
    if (exp) exp.onclick = () => document.querySelectorAll('#demonstrativo_tree details').forEach(d => d.open = true);
    if (col) col.onclick = () => document.querySelectorAll('#demonstrativo_tree details').forEach(d => d.open = false);
  }

  // API global esperada pelo index.html
  window.DemonstrativoTree = {
    refresh: () => render()
  };

  document.addEventListener('DOMContentLoaded', () => {
    bindControls();
    render();
  });
})();
