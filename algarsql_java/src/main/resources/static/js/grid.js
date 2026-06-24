/*
    ==========================================================================================------------------------------------
    comment: Componente de grade de dados com paginacao
    ==========================================================================================------------------------------------
*/

class TGrid {
    constructor(idTable, options = { "fetch": false, "edit": false, "export": false }) {
        this.idTable = idTable;
        this.options = options;
        this.fetch_on_next_button = false;
        this.tabela = document.getElementById(this.idTable);
        this.pager = document.getElementById(this.idTable + "_pager");
        this.prepareControl();
    }


    setContent(dados, columns, columns_types, limit_per_page = 5, actions = [], sql = "") {
        this.columns = ["#"].concat(columns);
        this.columns_types = columns_types;
        this.colunasSemRownum = columns;
        this.dados = dados;
        this.actions = actions;
        this.limit_per_page = limit_per_page;
        this.sql = sql;
        this.paginaAtual = 1;
        this.totalPaginas = Math.ceil(this.dados.length / this.limit_per_page);
    }

    copiarSelecionados() {
        const linhas     = this.tabela.querySelectorAll("tr");
        let   texto      = "";
        let   temSelecao = false;

        linhas.forEach((tr) => {
            const selecionados = tr.querySelectorAll(".th_selected");

            if (selecionados.length > 0) {
                temSelecao = true;
                let linhaTexto = Array.from(selecionados)
                    .map(td => td.innerText.trim())
                    .join("\t");
                texto += linhaTexto + "\n";
            }
        });

        if (!temSelecao) {
            this.report.innerHTML = 'No data Selected!';
            return;
        }

        try {
            copyToClip(texto);
            this.report.innerHTML =  'Copied to Clipboard!';
        } catch (err) {
            alert(err);
        }
    }


    selectColumn(colIndex, th) {
        if (colIndex == -1) {
            this.tabela.querySelectorAll("td.th_selected").forEach(td => td.classList.remove("th_selected"));
            return;
        }
        if (colIndex == 0) {
            this.tabela.querySelectorAll("td").forEach( (td,idx) => {
                if (td.cellIndex == 0) return;
                td.classList.add("th_selected");
            });
            return;
        }
        this.tabela.querySelectorAll("tr")
            .forEach( (c, idx) => {
                if (idx == 0) return; // pula header
                if ( th.selected ) {
                    c.cells[colIndex].classList.remove("th_selected");
                } else {
                    c.cells[colIndex].classList.add("th_selected");

                }
            });
        th.selected = !th.selected;
        this.generateStats();        
    }

    configuraResize(th, resizer) {
        let startX;
        let startWidth;
        let startTableWidth;

        const table = th.closest("table");

        resizer.addEventListener("mousedown", (e) => {
            startX = e.pageX;
            startWidth = th.offsetWidth;
            startTableWidth = table.offsetWidth;
            document.body.style.cursor = "col-resize";
            document.body.style.userSelect = "none";
            document.addEventListener("mousemove", mouseMove);
            document.addEventListener("mouseup", mouseUp);

        });

        function mouseMove(e) {
            const diff = e.pageX - startX;
            const newWidth = startWidth + diff;
            if (newWidth > 50) {
                th.style.width = newWidth + "px";
                table.style.width = (startTableWidth + diff) + "px";
            }
        }

        function mouseUp() {
            document.body.style.cursor = "";
            document.body.style.userSelect = "";
            document.removeEventListener("mousemove", mouseMove);
            document.removeEventListener("mouseup", mouseUp);
        }
    }

    selectCell(td, ctrlKey) {
        if (!ctrlKey) {
            this.tabela
                .querySelectorAll(".th_selected")
                .forEach(c => c.classList.remove("th_selected"));
        }

        td.classList.toggle("th_selected");
        this.report.innerHTML = "";
    }

    desenharTabela() {
        this.tabela.innerHTML = "";
        this.tabela.style.tableLayout = 'fixed';
        this.tabela.style.display = '';

        // Cabecalho
        const thead     = this.tabela.createTHead();
        const headerRow = thead.insertRow();
        this.columns.forEach( (c, colIndex) => {
            const th = document.createElement("th");
            th.textContent = c;
            th.selected    = false;
            th.onclick = () => this.selectColumn(colIndex, th);
            th.style.cursor = 'pointer';
            headerRow.appendChild(th);
            if (colIndex > 0) {
                const rs = document.createElement("div");
                rs.className = 'resizer';
                th.appendChild(rs);
                this.configuraResize(th, rs);
            } else {
                th.style.width = '50px';
            }
        });
        this.headerRow = headerRow;
        this.tabela.style.width = (this.columns.length * 150) + 'px';


        if (this.actions.length > 0) {
            const th = document.createElement("th");
            th.textContent = "#";
            headerRow.appendChild(th);
        }


        // Linhas
        const tbody = this.tabela.createTBody();
        const inicio = (this.paginaAtual - 1) * this.limit_per_page;
        const fim = inicio + this.limit_per_page;
        const linhas = this.dados.slice(inicio, fim);

        linhas.forEach((linha, idx) => {
            const tr = tbody.insertRow();

            // ROWNUM botao
            const tdRownum = tr.insertCell();
            const rownum = inicio + idx + 1;
            tdRownum.innerHTML = rownum;
            if (this.options.edit) {
                tdRownum.style.cursor = 'pointer';
                tdRownum.onclick = () => js_db_grid_editrow(tr, this.columns, this.columns_types);
            }

            // Cria células a partir das chaves especificadas em colunasSemRownum
            this.colunasSemRownum.forEach((col, idx_td) => {
                const td = tr.insertCell();

                td.textContent = linha[col] ?? "";
                td.value = linha[col] ?? "";
                td.onclick = (e) => this.selectCell(td, e.ctrlKey); 
                td.style.userSelect = 'none';

                if ( this.columns_types[idx_td].includes("PRE") && td.value !== "") {
                    td.addEventListener("mousemove", (e) => {
                        id_tooltip.style.display = "block";
                        id_tooltip.style.left = (e.pageX + 10) + "px";
                        id_tooltip.style.top = (e.pageY + 10) + "px";
                        id_tooltip.innerHTML = `<pre>${td.value}</pre>`;
                    });

                    td.addEventListener("mouseleave", () => {
                        id_tooltip.style.display = "none";
                    });                    
                }

                if ( this.columns_types[idx_td].includes("LOB") && td.value !== "") {
                    td.innerHTML = '';
                    const link = document.createElement('a');
                    link.textContent = '[LOB]';
                    link.href = '#';
                    link.onclick = (e) => {
                        e.preventDefault(); 
                        js_window_popup('VIEW CELL', td.value)
                    };
                    td.appendChild(link);                    
                }
            });

            if (this.actions.length > 0) {
                const tdAcoes = tr.insertCell();

                this.actions.forEach(acao => {
                    const link = document.createElement('a');
                    link.textContent = acao.texto;
                    link.href = '#';
                    link.style.marginRight = "10px";
                    link.onclick = (e) => {
                        e.preventDefault();
                        acao.funcao(linha);
                    };

                    tdAcoes.appendChild(link);
                });
            }

        });
        this.desenharPaginacao();
    }

    desenharPaginacao() {
        this.pager.innerHTML = "";

        if (this.dados.length === 0) {
            return;
        }

        this.totalPaginas = Math.ceil(this.dados.length / this.limit_per_page);

        const btnPrev       = document.createElement("button");
        btnPrev.textContent = "Prior";
        btnPrev.disabled    = this.paginaAtual === 1;
        btnPrev.onclick     = () => { this.paginaAtual--; this.desenharTabela(); };
        this.pager.appendChild(btnPrev);

        const info = document.createElement("span");
        info.textContent = ` Page ${this.paginaAtual} / ${this.totalPaginas} `;
        this.pager.appendChild(info);

        this.btnNext             = document.createElement("button");
        this.btnNext.textContent = "Next";
        this.btnNext.disabled    = !this.fetch_on_next_button && this.paginaAtual === this.totalPaginas;
        this.btnNext.onclick     = () => { 
            if (this.paginaAtual < this.totalPaginas) {
                this.paginaAtual++; 
                this.desenharTabela(); 
            } else {
                if ( this.fetch_on_next_button ) {
                    js_db_fetch50(this);
                }
            }
        };

        this.pager.appendChild(this.btnNext);

        if (this.options.export) {
            ["insert", "csv", "excel", "copy"].forEach((txt, i) => {
                const btn = document.createElement("button");
                btn.textContent = txt;
                if ( txt == "copy" ) {
                    btn.onclick = () => this.copiarSelecionados();
                } else {
                    btn.onclick = () => jsExportToFile(this.sql, i);
                }
                this.pager.appendChild(btn);
            });
        }

        if (this.options.fetch) {
            const btnFetch = document.createElement("button");
            btnFetch.textContent = "all";
            btnFetch.onclick = () => { js_db_fetch(); };
            this.pager.appendChild(btnFetch);
        }
        this.report = document.createElement("span");
        this.report.style.padding    = '10px';
        this.report.style.color      = 'red';
        this.report.style.fontWeight = 'bold';
        this.pager.appendChild(this.report);
    }


    prepareControl() {
        let selecting = false;
        let startCell = null;

        const selectRange = (cell1, cell2) => {
            const r1 = cell1.parentElement.rowIndex;
            const c1 = cell1.cellIndex;

            const r2 = cell2.parentElement.rowIndex;
            const c2 = cell2.cellIndex;

            const minR = Math.min(r1, r2);
            const maxR = Math.max(r1, r2);

            const minC = Math.min(c1, c2);
            const maxC = Math.max(c1, c2);

            for (let r = minR; r <= maxR; r++) {
                const row = this.tabela.rows[r];

                for (let c = minC; c <= maxC; c++) {
                    row.cells[c]?.classList.add("th_selected");
                }
            }
            this.generateStats();
        };

        this.tabela.addEventListener("mousedown", (e) => {
            const td = e.target.closest("td");
            if (!td /*|| !e.ctrlKey*/) return;
            selecting = true;
            startCell = td;
            td.classList.add("th_selected");
            e.preventDefault();
            this.tabela.focus();
        });

        document.addEventListener("mousemove", (e) => {
            if (!selecting) return;
            this.selectColumn(-1, null);
            const el = document.elementFromPoint(e.clientX, e.clientY);
            const td = el?.closest("td");
            if (!td || !this.tabela.contains(td)) return;
            selectRange(startCell, td);
        });

        document.addEventListener("mouseup", () => {
            selecting = false;
            startCell = null;
        });

        this.tabela.tabIndex = 0; // permite receber foco

        this.tabela.addEventListener("keydown", (e) => {
            if (e.ctrlKey && e.key.toLowerCase() === "c") {
                e.preventDefault();
                this.copiarSelecionados();
            }
        });        
    }



    generateStats() {
        this.report.innerHTML = '';

        const cells = Array.from(
            this.tabela.querySelectorAll("td.th_selected")
        );

        if (cells.length === 0) {
            return;
        }

        // Verifica se todas as células pertencem à mesma coluna
        const coluna = cells[0].cellIndex;

        if (!cells.every(cell => cell.cellIndex === coluna)) {
            return;
        }

        const valores = [];

        for (const cell of cells) {
            const valor = Number(cell.innerText.trim());
            if (isNaN(valor)) {
                return; 
            }
            valores.push(valor);
        }
        let soma  = valores.reduce((a, b) => a + b, 0);
        let menor = Math.min(...valores);
        let maior = Math.max(...valores);
        let qtd   = valores.length;

        this.report.innerHTML = ` [ sum=${soma} min=${menor} max=${maior} count=${qtd} ] `;
    }    
    

}