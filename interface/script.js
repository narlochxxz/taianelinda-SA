
const abas = [...document.querySelectorAll('[role="tab"]')];
const paineis = [...document.querySelectorAll('[role="tabpanel"]')];
const nomesAbas = abas.map(a => a.dataset.aba);

function mostrarAba(nome, focar = false) {
    if (!nomesAbas.includes(nome)) nome = "ordens";
    abas.forEach(aba => {
        const ativa = aba.dataset.aba === nome;
        aba.setAttribute("aria-selected", ativa);
        aba.tabIndex = ativa ? 0 : -1;
        if (ativa && focar) aba.focus();
    });
    paineis.forEach(p => { p.hidden = p.id !== "painel-" + nome; });
    history.replaceState(null, "", "#" + nome);
}

abas.forEach((aba, i) => {
    aba.addEventListener("click", () => mostrarAba(aba.dataset.aba));
    // Setas do teclado trocam de aba
    aba.addEventListener("keydown", e => {
        let alvo = null;
        if (e.key === "ArrowRight") alvo = (i + 1) % abas.length;
        if (e.key === "ArrowLeft") alvo = (i - 1 + abas.length) % abas.length;
        if (alvo !== null) { e.preventDefault(); mostrarAba(nomesAbas[alvo], true); }
    });
});
//estudar esta parte de cima, não entendi nada


// Depois de enviar um formulário, a página recarrega: lembra qual aba abrir
document.querySelectorAll("form[data-destino]").forEach(f => {
    f.addEventListener("submit", () => sessionStorage.setItem("aba-destino", f.dataset.destino));
});

// Trocar o status envia o formulário da linha (e volta para a aba de ordens)
document.querySelectorAll(".form-status select").forEach(sel => {
    sel.addEventListener("change", () => {
        sessionStorage.setItem("aba-destino", "ordens");
        sel.form.submit();
    });
});

// Qual aba abrir ao carregar: erro de formulário > destino salvo > endereço (#) > ordens
const doServidor = document.querySelector("main").dataset.abaInicial;
const destino = sessionStorage.getItem("aba-destino");
sessionStorage.removeItem("aba-destino");
mostrarAba(doServidor || destino || location.hash.slice(1) || "ordens");

// ---------- Campos ----------
// Placa sempre em maiúsculas enquanto digita
const placa = document.getElementById("placa");
placa.addEventListener("input", () => { placa.value = placa.value.toUpperCase(); });

// Telefone com máscara: (47) 99999-1234 ou (47) 3333-4444
const telefone = document.getElementById("telefone");
telefone.addEventListener("input", () => {
    const d = telefone.value.replace(/\D/g, "").slice(0, 11);
    let t = d;
    if (d.length > 10) t = `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
    else if (d.length > 6) t = `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    else if (d.length > 2) t = `(${d.slice(0, 2)}) ${d.slice(2)}`;
    telefone.value = t;
});

// Prévia do total (mão de obra + peças), no mesmo formato do servidor
function lerValor(texto) {
    texto = texto.trim();
    if (texto.includes(",")) texto = texto.replace(/\./g, "").replace(",", ".");
    const n = parseFloat(texto);
    return Number.isFinite(n) && n >= 0 ? n : 0;
}
const maoDeObra = document.getElementById("mao-de-obra");
const pecas = document.getElementById("pecas");
const previa = document.getElementById("previa-total");

function atualizarPrevia() {
    const total = lerValor(maoDeObra.value) + lerValor(pecas.value);
    previa.textContent = "Total: " + total.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
maoDeObra.addEventListener("input", atualizarPrevia);
pecas.addEventListener("input", atualizarPrevia);
atualizarPrevia();

// Avisos de sucesso somem sozinhos depois de alguns segundos
setTimeout(() => document.querySelectorAll(".aviso-sucesso").forEach(a => a.remove()), 6000);

// ---------- Filtro das ordens: busca por texto + chips de status ----------
const busca = document.getElementById("busca");
const chips = document.querySelectorAll(".chip");
const linhas = document.querySelectorAll("#tabela-ordens tbody tr[data-status]");
const linhaVazia = document.getElementById("linha-vazia");
let filtroStatus = "";

function aplicarFiltros() {
    const termo = busca.value.trim().toLowerCase();
    let visiveis = 0;
    linhas.forEach(l => {
        const ok = (!filtroStatus || l.dataset.status === filtroStatus)
                && (!termo || l.dataset.texto.includes(termo));
        l.hidden = !ok;
        if (ok) visiveis++;
    });
    linhaVazia.hidden = visiveis > 0 || linhas.length === 0;
}

busca.addEventListener("input", aplicarFiltros);
chips.forEach(chip => chip.addEventListener("click", () => {
    chips.forEach(c => c.classList.remove("ativo"));
    chip.classList.add("ativo");
    filtroStatus = chip.dataset.filtro;
    aplicarFiltros();
}));
