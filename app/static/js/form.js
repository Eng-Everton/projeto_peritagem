/**
 * Gerenciamento dinâmico de componentes e fotos no formulário de Peritagem KGF.
 */

function add_componente() {
    const container = document.getElementById("container-componentes");
    const div = document.createElement("div");
    div.className = "componente-bloco";

    div.innerHTML = `
        <div class="componente-header">
            <h3 class="componente-titulo">Componente</h3>
            <button type="button" class="btn-remove" onclick="remover_componente(this)">Remover</button>
        </div>
        <label>Nome do Componente:</label>
        <input type="text" name="comp_nome[]" placeholder="Ex: Haste, Camisa, Êmbolo..." required>

        <div class="row">
            <div class="col">
                <label>Dimensionamento:</label>
                <textarea name="comp_dim[]" rows="3"></textarea>
            </div>
            <div class="col">
                <label>Avaria:</label>
                <textarea name="comp_avaria[]" rows="3" class="textarea-avaria" placeholder="Descreva os danos encontrados..."></textarea>
            </div>
        </div>

        <label>Serviço a ser Executado:</label>
        <input type="text" name="comp_servico[]" placeholder="Ex: Cromo e Retífica">

        <div class="foto-container">
            <label>Fotos (Câmera ou Galeria):</label>
            <input type="file" class="input-foto-comp" accept="image/*" capture="camera" multiple>
        </div>
        <button type="button" class="btn-foto" onclick="add_foto_input(this)">+ Adicionar outra foto neste item</button>
    `;

    container.appendChild(div);
    reindexar_componentes();
}

function add_foto_input(botao) {
    const bloco = botao.closest(".componente-bloco");
    const containerFotos = bloco.querySelector(".foto-container");
    const input = document.createElement("input");
    input.type = "file";
    input.className = "input-foto-comp foto-input-extra";
    input.accept = "image/*";
    input.capture = "camera";
    input.multiple = true;
    containerFotos.appendChild(input);
    reindexar_componentes();
}

function remover_componente(botao) {
    const container = document.getElementById("container-componentes");
    const blocos = container.querySelectorAll(".componente-bloco");
    if (blocos.length <= 1) {
        return;
    }
    const bloco = botao.closest(".componente-bloco");
    bloco.remove();
    reindexar_componentes();
}

function reindexar_componentes() {
    const container = document.getElementById("container-componentes");
    const blocos = container.querySelectorAll(".componente-bloco");

    blocos.forEach((bloco, index) => {
        const num = index + 1;
        const titulo = bloco.querySelector(".componente-titulo");
        if (titulo) {
            titulo.textContent = `Componente #${num}`;
        }

        const btnRemove = bloco.querySelector(".btn-remove");
        if (btnRemove) {
            btnRemove.style.display = blocos.length > 1 ? "inline-block" : "none";
        }

        const inputsFoto = bloco.querySelectorAll(".input-foto-comp");
        inputsFoto.forEach((input) => {
            input.name = `comp_foto_${num}[]`;
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    add_componente();
});

