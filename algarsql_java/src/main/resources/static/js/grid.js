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
        this.tabela = document.getElementById(this.idTable);
        this.pager = document.getElementById(this.idTable + "_pager");
        this.prepareControl();
    }

    getCellValueByHeader(row, headerName) {
        let index = -1;

        this.headerRow.forEach((th, i) => {
            if (th.textContent.trim() === headerName) {
                index = i;
            }
        });

        if (index === -1) return null;

        return row.cells[index]?.innerText || null;
    }

    copiarSelecionados() {
        const linhas = this.tabela.querySelectorAll("tr");

        let texto = "";
        let temSelecao = false;

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
            alert('No data Selected!');
            return;
        }

        try {
            copyToClip(texto);
        } catch (err) {
            alert(err);
        }
    }


    selectColumn(colIndex) {
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
                c.cells[colIndex].classList.toggle("th_selected");
            });
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
            th.onclick = () => this.selectColumn(colIndex);
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
                td.onclick = (e) => this.selectCell(td, e.ctrlKey); //this.selectColumn(-1);

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
    }


    prepareControl() {
        let selecting = false;
        this.tabela.addEventListener("mousedown", (e) => {
            const td = e.target.closest("td");
            if (!td || !e.ctrlKey) return;
            selecting = true;
            td.classList.toggle("th_selected");
        });
        this.tabela.addEventListener("mouseover", (e) => {
            if (!selecting) return;
            const td = e.target.closest("td");
            if (td) {
                td.classList.add("th_selected");
            }
        });
        document.addEventListener("mouseup", () => {
            selecting = false;
        });        
    }
}