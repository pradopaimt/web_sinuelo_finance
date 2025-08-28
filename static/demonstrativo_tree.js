(function(){
  const CSS = `:root{--bg:#0f172a;--panel:#111827;--muted:#94a3b8;--text:#e5e7eb;--accent:#22c55e;--border:#1f2937;--hover:#0b1222;--info:#93c5fd}*{box-sizing:border-box} .sf-card{background:rgba(17,24,39,.75);border:1px solid var(--border);border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.25);backdrop-filter:blur(6px)} .sf-header{padding:16px 20px;display:flex;gap:12px;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border)} .sf-title{font-size:18px;margin:0;font-weight:600;color:var(--text)} .sf-controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:flex-end} .sf-group{display:flex;align-items:center;gap:8px;background:#0b1222;border:1px solid var(--border);padding:8px 10px;border-radius:12px} .sf-group .title{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em} .sf-pill{display:inline-flex;align-items:center;gap:8px;background:#0b1222;border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:999px;cursor:pointer;user-select:none} .sf-pill input{accent-color:var(--accent)} .sf-btn{background:#0b1222;border:1px solid var(--border);color:var(--text);padding:8px 12px;border-radius:10px;cursor:pointer} .sf-btn:hover{background:#0d162b} .sf-select{background:#0b1222;color:var(--text);border:1px solid var(--border);border-radius:10px;padding:6px 8px} .sf-content{padding:8px 8px 12px} table.sf{width:100%;border-collapse:collapse;font-size:14px} table.sf thead th{text-align:left;font-weight:600;color:var(--muted);padding:10px 8px;border-bottom:1px solid var(--border)} table.sf tbody td{padding:8px;border-bottom:1px dashed #162033} .sf-name{display:flex;align-items:center;gap:8px} .sf-toggle{width:22px;height:22px;border-radius:6px;border:1px solid var(--border);display:inline-grid;place-items:center;cursor:pointer;background:#0b1222;color:var(--muted);font-weight:700;user-select:none} .sf-toggle:hover{background:#0d162b} .indent-0{padding-left:0}.indent-1{padding-left:20px}.indent-2{padding-left:40px}.indent-3{padding-left:60px} .sf-badge{display:inline-block;background:rgba(34,197,94,.15);color:#86efac;border:1px solid rgba(34,197,94,.4);padding:2px 8px;border-radius:999px;font-size:12px} .sf-note{color:var(--muted);font-size:12px;padding:10px 12px} .sf-kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;padding:12px;border-bottom:1px solid var(--border)} .sf-kpi .box{background:#0b1222;border:1px solid var(--border);border-radius:12px;padding:12px} .sf-kpi .box h3{margin:0 0 6px;font-size:12px;color:var(--muted);font-weight:600} .sf-kpi .box div{font-size:16px;font-weight:700} tfoot td{font-weight:700;border-top:1px solid var(--border);padding-top:10px} @media (max-width:720px){.sf-kpi{grid-template-columns:1fr 1fr}.sf-header{align-items:start;flex-direction:column;gap:12px}.sf-controls{justify-content:flex-start}.sf-group{width:100%;flex-wrap:wrap}}`;

  const mockData = [
    { natureza:"Receita Operacional", items:[{categoria:"Vendas", items:[{conta:"Venda Gado Corte", ccValues:{"CC – Cria":125000, "CC – Recria":88000}, flags:{impostoRenda:false}, periodo:{safra:"24-25", ano:2025}}, {conta:"Venda Bezerros", ccValues:{"CC – Cria":54000, "CC – Recria":22000}, flags:{impostoRenda:false}, periodo:{safra:"24-25", ano:2025}}]}, {categoria:"Serviços", items:[{conta:"Arrendamento", ccValues:{"CC – Geral":12000}, flags:{impostoRenda:true}, periodo:{safra:"24-25", ano:2025}}]}]},
    { natureza:"Receita Não Operacional", items:[{categoria:"Financeiras", items:[{conta:"Juros Recebidos", ccValues:{"CC – Geral":3500}, flags:{impostoRenda:true}, periodo:{safra:"24-25", ano:2025}}]}]},
    { natureza:"Despesa Operacional", items:[{categoria:"Nutrição", items:[{conta:"Ração", ccValues:{"CC – Recria":38000, "CC – Engorda":21000}, flags:{impostoRenda:false}, periodo:{safra:"24-25", ano:2025}}, {conta:"Sal Mineral", ccValues:{"CC – Cria":9000, "CC – Recria":6000}, flags:{impostoRenda:false}, periodo:{safra:"24-25", ano:2025}}]}, {categoria:"Sanidade", items:[{conta:"Vacinas", ccValues:{"CC – Cria":4500, "CC – Recria":4100}, flags:{impostoRenda:false}, periodo:{safra:"24-25", ano:2025}}]}]},
    { natureza:"Despesa Não Operacional", items:[{categoria:"Financeiras", items:[{conta:"Juros Pagos", ccValues:{"CC – Geral":4200}, flags:{impostoRenda:true}, periodo:{safra:"24-25", ano:2025}}]}, {categoria:"Administrativas", items:[{conta:"Contabilidade", ccValues:{"CC – Geral":7000}, flags:{impostoRenda:true}, periodo:{safra:"24-25", ano:2025}}]}]}
  ];

  const formatBRL = v => (Number(v)||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
  const slugify = str => String(str).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^\w\s-]/g,'').trim().replace(/\s+/g,'-').toLowerCase();
  function extractCostCenters(data){ const set = new Set(); const walk=n=>{ if(n.ccValues) Object.keys(n.ccValues).forEach(cc=>set.add(cc)); if(n.items) n.items.forEach(walk); }; data.forEach(walk); return Array.from(set).sort(); }
function passesFilters(node, st) {
    if (st.filterIR && node.ccValues && !(node.flags && node.flags.impostoRenda)) return false;

    if (node.ccValues && st.periodType && st.periodValue) {
    const p = node.periodo || {};
    const want = String(st.periodValue);

    const matches = (val) => {
      if (val == null) return false;
      if (Array.isArray(val) || val instanceof Set) {
        return Array.from(val).map(String).includes(want);
      }
      return String(val) === want;
    };

    if (st.periodType === 'safra' && !matches(p.safra)) return false;
    if (st.periodType === 'ano'   && !matches(p.ano))   return false;
    if (st.periodType === 'mes'   && !matches(p.mes))   return false;
  }

  return true;
}

  function calcNodeTotal(node, selectedCCs, st){ if(!passesFilters(node,st)) return 0; if(node.ccValues){ return Object.entries(node.ccValues).filter(([cc])=>selectedCCs.has(cc)).reduce((s,[,v])=>s+(Number(v)||0),0);} if(node.items){ return node.items.reduce((s,ch)=>s+calcNodeTotal(ch,selectedCCs,st),0);} return 0; }
 function discoverSafrasAndAnos(data){ 
  const safras=new Set(), anos=new Set(), meses=new Set();
  const addMany = (v, bag) => {
    if (v == null) return;
    if (Array.isArray(v) || v instanceof Set) { for (const x of v) bag.add(String(x)); }
    else bag.add(String(v));
  };
  const walk = n => {
    if (n.periodo){
      addMany(n.periodo.safra, safras);
      addMany(n.periodo.ano,   anos);
      addMany(n.periodo.mes,   meses);
    }
    if (n.items) n.items.forEach(walk);
  };
  data.forEach(walk);

  const sortSmart = arr => arr.slice().sort((a,b)=>{
    const re=/^\d{4}-\d{1,2}$/;
    if(re.test(a) && re.test(b)) return new Date(a+'-01') - new Date(b+'-01');
    const na=Number(a), nb=Number(b);
    if(!Number.isNaN(na) && !Number.isNaN(nb)) return na-nb;
    return String(a).localeCompare(String(b));
  });

  return { safras: sortSmart([...safras]), anos: sortSmart([...anos]), meses: sortSmart([...meses]) };
}

  function ensureStyle(){ if(document.getElementById('sf-tree-style')) return; const s=document.createElement('style'); s.id='sf-tree-style'; s.textContent=CSS; document.head.appendChild(s); }

  function mount(root, opts={}){
    ensureStyle();
    const el = typeof root==='string'? document.querySelector(root) : root;
    if(!el) throw new Error('Container não encontrado');

    const state = {
      data: [],
      costCenters: [],
      selectedCCs: new Set(),
      expanded: new Set(),
      periodType: 'safra',
      periodValue: '',
      filterIR: false,
    };

    const html = `
      <div class="sf-card">
        <div class="sf-header">
          <h1 class="sf-title">Demonstrativo por Natureza — Visão em Árvore</h1>
          <div class="sf-controls" id="sf-controls"></div>
        </div>
        <div class="sf-kpi" id="sf-kpis"></div>
        <div class="sf-content">
          <table class="sf" id="sf-table">
            <thead>
              <tr><th>Natureza</th><th style="width:180px;">Total (R$)</th><th style="width:140px;">% da Natureza</th></tr>
            </thead>
            <tbody id="sf-tbody"></tbody>
            <tfoot>
              <tr id="sf-resultado-row" style="display:none;">
                <td class="sf-name"><span class="sf-badge">resultado</span><span style="margin-left:4px;font-weight:700;">Resultado</span></td>
                <td id="sf-resultado-total" style="text-align:right;">R$ 0,00</td>
                <td id="sf-resultado-pct" style="text-align:right;color:var(--info);">0%</td>
              </tr>
            </tfoot>
          </table>
          <div class="sf-note">Clique em <span class="sf-badge">+</span> para expandir e <span class="sf-badge">−</span> para recolher. "Resultado" = (Receitas − Despesas); % sobre Receitas.</div>
        </div>
      </div>`;
    el.innerHTML = html;

    const refs = {
      controls: el.querySelector('#sf-controls'),
      kpis: el.querySelector('#sf-kpis'),
      tbody: el.querySelector('#sf-tbody'),
      resRow: el.querySelector('#sf-resultado-row'),
      resTotal: el.querySelector('#sf-resultado-total'),
      resPct: el.querySelector('#sf-resultado-pct'),
    };

    function setData(data, ccList){
      state.data = Array.isArray(data)? data : [];
      state.costCenters = ccList && ccList.length? ccList : extractCostCenters(state.data);
      state.selectedCCs = new Set(state.costCenters);
	const { safras, anos, meses } = discoverSafrasAndAnos(state.data);
	state.periodType = safras.length ? 'safra': (anos.length ? 'ano' : (meses.length ? 'mes' : 'safra'));

	state.periodValue =
	state.periodType === 'safra' ? (safras[0] || '') :
	state.periodType === 'ano'   ? (anos[0]   || '') :
	state.periodType === 'mes'   ? (String(meses[0]) || '') :
  '';
 state.expanded.clear();
      renderAll();
    }

    function renderAll(){ renderControls(); renderKPIs(); renderTree(); }

    function renderControls(){
      const elc = refs.controls; elc.innerHTML = '';
      // CCs
      const gCC = document.createElement('div'); gCC.className='sf-group'; gCC.innerHTML = `<span class="title">Centro de custo</span>`;
      const allId = 'sf-cc-all';
      const pillAll = document.createElement('label'); pillAll.className='sf-pill'; pillAll.innerHTML = `<input type="checkbox" id="${allId}" ${state.selectedCCs.size===state.costCenters.length?'checked':''}/> Selecionar todos os CCs`;
      pillAll.querySelector('input').addEventListener('change',e=>{ state.selectedCCs = e.target.checked? new Set(state.costCenters) : new Set(); renderAll();});
      gCC.appendChild(pillAll);
      state.costCenters.forEach((cc,i)=>{ const id=`sf-cc-${i}`; const p=document.createElement('label'); p.className='sf-pill'; p.innerHTML=`<input type="checkbox" id="${id}" ${state.selectedCCs.has(cc)?'checked':''}/> ${cc}`; p.querySelector('input').addEventListener('change',e=>{ if(e.target.checked) state.selectedCCs.add(cc); else state.selectedCCs.delete(cc); const all=document.getElementById(allId); if(all) all.checked = state.selectedCCs.size===state.costCenters.length; renderAll();}); gCC.appendChild(p); });
      elc.appendChild(gCC);

      // Período
      const gP = document.createElement('div'); gP.className='sf-group';
     gP.innerHTML = `<span class="title">Período</span>
		<label class="sf-pill">
		<input type="radio" name="sf-period" value="safra" ${state.periodType==='safra'?'checked':''}/> Safra
		</label>
		<label class="sf-pill">
		<input type="radio" name="sf-period" value="ano" ${state.periodType==='ano'?'checked':''}/> Ano
		</label>
		<label class="sf-pill">
		<input type="radio" name="sf-period" value="mes" ${state.periodType==='mes'?'checked':''}/> Mês
		</label>
		<select id="sf-period" class="sf-select"></select>`;
      elc.appendChild(gP);
      gP.querySelectorAll('input[name="sf-period"]').forEach(r=>r.addEventListener('change',e=>{ state.periodType=e.target.value; populatePeriodOptions(gP.querySelector('#sf-period')); renderAll(); }));
      populatePeriodOptions(gP.querySelector('#sf-period'));
      gP.querySelector('#sf-period').value = String(state.periodValue);
      gP.querySelector('#sf-period').addEventListener('change',e=>{ state.periodValue=e.target.value; renderAll(); });

      // IR
      const gIR = document.createElement('div'); gIR.className='sf-group'; gIR.innerHTML = `<span class="title">Filtro</span>
        <label class="sf-pill"><input type="checkbox" id="sf-ir" ${state.filterIR?'checked':''}/> Somente "Imposto de Renda"</label>`;
      gIR.querySelector('#sf-ir').addEventListener('change',e=>{ state.filterIR=e.target.checked; renderAll(); });
      elc.appendChild(gIR);

      // Expand/Collapse
      const gX = document.createElement('div'); gX.className='sf-group';
      const ex = document.createElement('button'); ex.className='sf-btn'; ex.textContent='Expandir tudo'; ex.onclick=()=>{ collectAllRowIds().forEach(id=>state.expanded.add(id)); renderAll(); };
      const cl = document.createElement('button'); cl.className='sf-btn'; cl.textContent='Recolher tudo'; cl.onclick=()=>{ state.expanded.clear(); renderAll(); };
      gX.appendChild(ex); gX.appendChild(cl); elc.appendChild(gX);
    }

	function populatePeriodOptions(sel){ 
  sel.innerHTML='';
  const {safras, anos, meses} = discoverSafrasAndAnos(state.data);
  let arr=[];
  if(state.periodType==='safra') arr = safras;
  else if(state.periodType==='ano') arr = anos;
  else if(state.periodType==='mes') arr = meses;

  const fmtLabel = (v)=>{
    const s=String(v);
    if(state.periodType==='mes'){
      if(/^\d{4}-\d{1,2}$/.test(s)) {
        return new Date(s+'-01').toLocaleDateString('pt-BR',{month:'long', year:'numeric'});
      }
      const n=Number(s);
      if(!Number.isNaN(n) && n>=1 && n<=12) {
        return new Date(2000,n-1,1).toLocaleDateString('pt-BR',{month:'long'});
      }
    }
    return s;
  };
    arr.forEach(v=>{
    const o=document.createElement('option');
    o.value = String(v);          // <-- sempre string
    o.textContent = fmtLabel(v);
    sel.appendChild(o);
  });

 if (!arr.map(String).includes(String(state.periodValue))) {
    state.periodValue = arr.length ? String(arr[0]) : '';
  }
  sel.value = String(state.periodValue);
}

function renderKPIs(){
  refs.kpis.innerHTML='';
  state.data.forEach(n=>{
    const total = calcNodeTotal(n, state.selectedCCs, state);
    const box = document.createElement('div');
    box.className = 'box';
    box.innerHTML = `<h3>${n.natureza}</h3><div>${formatBRL(total)}</div>`;
    refs.kpis.appendChild(box);
  });
}
    function collectAllRowIds(){ const ids=new Set(); state.data.forEach(n=>{ const nid=`nat-${slugify(n.natureza)}`; ids.add(nid); (n.items||[]).forEach(c=>{ const cid=`${nid}::cat-${slugify(c.categoria)}`; ids.add(cid); (c.items||[]).forEach(cta=>{ ids.add(`${cid}::cta-${slugify(cta.conta)}`); }); }); }); return ids; }

function row({ id, level, name, total, percent, expandable, isOpen }){
  const tr=document.createElement('tr'); tr.dataset.id=id; tr.dataset.level=level;
  const tdName=document.createElement('td'); tdName.className=`sf-name indent-${Math.min(level,3)}`;

  if(expandable){
    const t=document.createElement('span'); t.className='sf-toggle'; t.textContent=isOpen?'−':'+';
    t.setAttribute('role','button'); t.setAttribute('aria-expanded',String(isOpen));
    t.addEventListener('click',()=>{ if(isOpen) state.expanded.delete(id); else state.expanded.add(id); renderAll(); });
    tdName.appendChild(t);
  } 
  const nameSpan=document.createElement('span');
  nameSpan.textContent=name;
  nameSpan.style.fontWeight = level===0? '700' : (level===1? '600' : '500');
  nameSpan.style.marginLeft='4px';
  tdName.appendChild(nameSpan);

  const tdTotal=document.createElement('td'); tdTotal.textContent=formatBRL(total); tdTotal.style.textAlign='right'; tdTotal.style.fontWeight= level===0? '700' : '500';
  const tdPct=document.createElement('td'); tdPct.textContent=`${(percent*100).toFixed(1)}%`; tdPct.style.textAlign='right'; tdPct.style.color='var(--info)';
  tr.appendChild(tdName); tr.appendChild(tdTotal); tr.appendChild(tdPct);
  return tr;
}
    function renderTree(){
      refs.tbody.innerHTML=''; let totalReceitas=0, totalDespesas=0;
      state.data.forEach(n=>{
        const nid=`nat-${slugify(n.natureza)}`; const totalNat=calcNodeTotal(n,state.selectedCCs,state)||0;
        refs.tbody.appendChild(row({id:nid, level:0, name:n.natureza, total:totalNat, percent:1, expandable:!!(n.items&&n.items.length), isOpen:state.expanded.has(nid)}));
        if(String(n.natureza).toLowerCase().startsWith('receita')) totalReceitas+=totalNat;
        if(String(n.natureza).toLowerCase().startsWith('despesa')) totalDespesas+=totalNat;
        if(state.expanded.has(nid) && n.items){ n.items.forEach(c=>{ const cid=`${nid}::cat-${slugify(c.categoria)}`; const totalCat=calcNodeTotal(c,state.selectedCCs,state)||0; const pctCat= totalNat? totalCat/totalNat : 0; refs.tbody.appendChild(row({id:cid, level:1, name:c.categoria, total:totalCat, percent:pctCat, expandable:!!(c.items&&c.items.length), isOpen:state.expanded.has(cid)})); if(state.expanded.has(cid) && c.items){ c.items.forEach(cta=>{ const ctaId=`${cid}::cta-${slugify(cta.conta)}`; const totalCta=calcNodeTotal(cta,state.selectedCCs,state)||0; const pctCta= totalNat? totalCta/totalNat : 0; refs.tbody.appendChild(row({id:ctaId, level:2, name:cta.conta, total:totalCta, percent:pctCta, expandable:false, isOpen:false})); }); } }); }
      });
      const resultado = totalReceitas - totalDespesas; refs.resTotal.textContent=formatBRL(resultado); const pctRes = totalReceitas? (resultado/totalReceitas) : 0; refs.resPct.textContent=`${(pctRes*100).toFixed(1)}%`; refs.resRow.style.display='table-row';
    }

    // Inicialização
    (async function init(){
      const data = typeof opts.loadData === 'function' ? await opts.loadData() : mockData;
      setData(data, opts.costCenters || null);
    })();

    // Expor API pública para integração
    const api = {
      setData: (data, costCenters)=> setData(data, costCenters),
      setPeriodo: (tipo, valor)=>{ state.periodType=tipo; state.periodValue=valor; renderAll(); },
      setFiltroIR: on=>{ state.filterIR=!!on; renderAll(); },
      expandAll: ()=>{ collectAllRowIds().forEach(id=>state.expanded.add(id)); renderAll(); },
      collapseAll: ()=>{ state.expanded.clear(); renderAll(); }
    };

    el.__sfApi = api; // referencia local caso precise
    return api;
  }

  // API global
  window.DemonstrativoTreeWidget = {
    mount,
  };
})();
