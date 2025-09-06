async function listarSocios() {
  const resp = await fetch(`${API_BASE}/socios/`);
  if (!resp.ok) throw new Error("Erro ao buscar sócios");
  return await resp.json();
}

async function atualizarSaldo(id, valor) {
  await fetch(`${API_BASE}/socios/${id}/saldo_inicial`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ saldo_inicial: valor })
  });
  await carregarSocios(); // recarrega
}

async function listarExtrato(id, start = null, end = null) {
  let url = `${API_BASE}/socios/${id}/extrato`;
  if (start || end) {
    const params = [];
    if (start) params.push(`start=${start}`);
    if (end) params.push(`end=${end}`);
    url += "?" + params.join("&");
  }
  const resp = await fetch(url);
  if (!resp.ok) throw new Error("Erro ao buscar extrato");
  return await resp.json();
}

async function mostrarExtrato(id, socios) {
  const socio = socios.find(s => String(s.id) === String(id));
  const saldoDiv = document.getElementById("saldoInicial");

  const anoAtual = new Date().getFullYear();
  const startDefault = `${anoAtual}-01`;
  const endDefault = `${anoAtual}-12`;

  // Só saldo inicial e filtros aqui
  saldoDiv.innerHTML = `
    <p><b>Saldo inicial:</b> R$ ${parseFloat(socio.saldo_inicial).toFixed(2)}</p>
    <div style="margin-top:8px">
      <label>De: <input type="month" id="filtroStart" value="${startDefault}"></label>
      <label>Até: <input type="month" id="filtroEnd" value="${endDefault}"></label>
      <button onclick="aplicarFiltro(${socio.id})">Aplicar filtro</button>
    </div>
  `;

  await carregarExtrato(id);  
}

async function carregarExtrato(id) {
  const start = document.getElementById("filtroStart")?.value || null;
  const end = document.getElementById("filtroEnd")?.value || null;
  const data = await listarExtrato(id, start, end);
  const extratoDiv = document.getElementById("extratoSocio");

  const rows = data.extrato.length > 0
    ? data.extrato.map(e => `
        <tr>
          <td>${e.mes}</td>
          <td>R$ ${e.entradas.toFixed(2)}</td>
          <td>R$ ${e.saidas.toFixed(2)}</td>
          <td><b>R$ ${e.saldo.toFixed(2)}</b></td>
        </tr>
      `).join("")
    : `<tr><td colspan="4">Nenhum lançamento no período</td></tr>`;

  // Novo saldo inicial vai no rodapé
  extratoDiv.innerHTML = `
    <h3>Extrato de ${data.socio}</h3>
    <table>
      <thead>
        <tr><th>Mês</th><th>Entradas</th><th>Saídas</th><th>Saldo acumulado</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    <div id="novoSaldoContainer" style="margin-top:12px; text-align:right;">
      <input type="number" id="novoSaldo" placeholder="Novo saldo" />
      <button onclick="atualizarSaldo(${id}, document.getElementById('novoSaldo').value)">
        Salvar saldo
      </button>
    </div>
  `;
}

function aplicarFiltro(id) {
  carregarExtrato(id);
}

async function carregarSocios() {
  const socios = await listarSocios();
  const div = document.getElementById("sociosConteudo");

  div.innerHTML = `
    <label for="socioSelect">Selecione o sócio:</label>
    <select id="socioSelect">
      ${socios.map(s => `<option value="${s.id}">${s.nome}</option>`).join("")}
    </select>
    <div id="saldoInicial"></div>
    <div id="extratoSocio"></div>
  `;

  // Seleciona Eduardo como padrão, se existir
  const select = document.getElementById("socioSelect");
  const eduardo = socios.find(s => s.nome.toUpperCase().includes("EDUARDO"));
  if (eduardo) {
    select.value = eduardo.id;
  }

  select.addEventListener("change", () => mostrarExtrato(select.value, socios));

  // Mostra o padrão
  mostrarExtrato(select.value, socios);
}

document.addEventListener("DOMContentLoaded", () => {
  const tab = document.querySelector('[data-tab="socios"]');
  if (tab) {
    tab.addEventListener("click", carregarSocios);
  }
});
