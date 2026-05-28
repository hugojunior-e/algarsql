let global_var = {};


function copyToClip(texto) {
    const textarea = document.createElement("textarea");
    textarea.value = texto.trim();
    textarea.style.position = "fixed"; // evita scroll
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    alert("Copy Success!");    
}

/*
    ==========================================================================================------------------------------------
    comment: Implementacao de um banco de dados local usando IndexedDB para armazenar dados temporarios, como a estrutura da arvore de objetos do banco de dados.
    Isso melhora a performance ao evitar consultas repetidas ao servidor para obter a mesma informacao.
    ==========================================================================================------------------------------------
*/

class LocalDB {
    constructor(dbName = "algarsql_db", version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
    }

    async openDB() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const req = indexedDB.open(this.dbName, this.version);

            req.onupgradeneeded = e => {
                const db = e.target.result;

                if (!db.objectStoreNames.contains("data")) {
                    db.createObjectStore("data", { keyPath: "id" });
                }
            };

            req.onsuccess = () => {
                this.db = req.result;
                resolve(this.db);
            };

            req.onerror = () => reject(req.error);
        });
    }

    async saveData(id, value) {
        const db = await this.openDB();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("data", "readwrite");
            const store = tx.objectStore("data");

            store.put({
                id: id,
                value: value,
                updated: Date.now()
            });

            tx.oncomplete = () => resolve(true);
            tx.onerror    = () => reject(tx.error);
        });
    }

    async loadData(id) {
        const db = await this.openDB();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("data", "readonly");
            const store = tx.objectStore("data");

            const req = store.get(id);

            req.onsuccess = () => resolve(req.result?.value ?? null);
            req.onerror   = () => reject(req.error);
        });
    }

    async deleteData(id) {
        const db = await this.openDB();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("data", "readwrite");
            tx.objectStore("data").delete(id);

            tx.oncomplete = () => resolve(true);
            tx.onerror    = () => reject(tx.error);
        });
    }

    async clear() {
        const db = await this.openDB();

        return new Promise((resolve, reject) => {
            const tx = db.transaction("data", "readwrite");
            tx.objectStore("data").clear();

            tx.oncomplete = () => resolve(true);
            tx.onerror    = () => reject(tx.error);
        });
    }
}


/*
    ==========================================================================================------------------------------------
    comment: Implementacao de um timer para medir o tempo decorrido entre o inicio e o fim de uma operacao, como a execucao de uma consulta SQL.
    ==========================================================================================------------------------------------
*/

class TTimer {
    constructor() {
        this.dt_inicio = null;
        this.dt_fim    = null;
    }

    start() {
        this.dt_inicio = new Date();
        this.dt_fim    = null;
        this.run();
    }
    
    run() {
        const d1 = this.dt_inicio;
        const d2 = this.dt_fim == null ? new Date() : this.dt_fim;
        let diffMs = Math.abs(d2 - d1);

        const horas = Math.floor(diffMs / (1000 * 60 * 60));
        diffMs %= (1000 * 60 * 60);

        const minutos = Math.floor(diffMs / (1000 * 60));
        diffMs %= (1000 * 60);

        const segundos = Math.floor(diffMs / 1000);
        const milissegundos = diffMs % 1000;

        const pad = (n, size = 2) => String(n).padStart(size, '0');

        id_menu_timer.innerHTML = `${pad(horas)}:${pad(minutos)}:${pad(segundos)}` + (this.dt_fim == null ? "" : `:${pad(milissegundos, 3)}`);

        if ( this.dt_fim == null ) {
            setTimeout(() => {
                this.run();
            }, 1000);
        }        
    }

    stop() {
        this.dt_fim = new Date();
    }
}

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

    desenharTabela() {
        this.tabela.innerHTML = "";
        this.tabela.style.tableLayout = 'fixed';

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
                td.onclick = () => this.selectColumn(-1);

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
}





/*
    ==========================================================================================------------------------------------ 
    comment: Funcao generica para realizar requisicoes AJAX ao servidor, com tratamento de sucesso e erro.
    ==========================================================================================------------------------------------
*/
function ajax(url, dataBody, jsAction = null, jsError = null, usingHeader = true) {
    var options = {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Tab-ID": global_var.session_id
            },
            body: new URLSearchParams(dataBody)
    };

    if ( usingHeader == false ) {
        options = {
            method: "POST",
            headers: {
                "X-Tab-ID": global_var.session_id
            },
            body: dataBody
        };
    }

    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then(a => {
            if (jsAction !== null) {
                jsAction(a);
            }
        })
        .catch(error => {
            if (jsError !== null) {
                jsError(error);
            } else {
                alert(error);
            }
        });
}

async function js_download(f) {
    try {
        const formData = new FormData();

        document.body.style.cursor = "wait";
        formData.append("filename", f);


        const response = await fetch("/download", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams(formData)
        });

        if (!response.ok) {
            throw new Error("Erro no download");
        }

        // Nome do arquivo vindo do Flask
        const disposition = response.headers.get("Content-Disposition");
        let filename = "download";

        if (disposition && disposition.includes("filename=")) {
            filename = disposition.split("filename=")[1].replace(/"/g, "");
        }

        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");

        a.href = url;
        a.download = filename;

        document.body.appendChild(a);
        a.click();

        a.remove();
        window.URL.revokeObjectURL(url);

    } catch (e) {
        console.error(e);
        alert("Erro ao baixar arquivo");
    } finally {
        document.body.style.cursor = "default";
    }
}


/*
    ==========================================================================================------------------------------------
    comment: Funcao para converter uma string de data no formato brasileiro (dd/mm/yyyy hh:mm:ss) em um objeto Date do JavaScript.
    ==========================================================================================-------------------------------------
*/


function gerar_alias(nomeTabela) {
    nomeTabela = nomeTabela.trim().toUpperCase();

    // Caso tenha _
    if (nomeTabela.includes("_")) {
        return nomeTabela
            .split("_")
            .map(p => p[0])
            .join("")
            .substring(0, 4)
            .toLowerCase();
    }

    // Sem _
    let primeira = nomeTabela[0];

    // Remove vogais, mas mantém a primeira letra
    let resto = nomeTabela
        .substring(1)
        .replace(/[AEIOU]/g, "");

    let alias = (primeira + resto)
        .substring(0, 4);

    // Se ficou pequeno, completa com o nome original
    if (alias.length < 3) {
        alias = nomeTabela.substring(0, 4);
    }

    return alias.toLowerCase();
}



function generate_session_id() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}


function change_icon(running = null) {
    let caption = id_login_username.value + "@" + id_login_database.options[id_login_database.selectedIndex].innerText;

    if (running == null ) {
        document.title        = "🔵 - AlgarSQL";
        id_menu_db.innerHTML  = "";
        id_tree_obj.innerHTML = '';
        id_tree_obj.index     = 0;
        return;
    }
    document.title       = (running ? "🔴" : "🔵") + " " + caption;
    id_menu_db.innerHTML = caption;        
}


async function js_monta_tree() {
    let ret1 = await global_var.cache.loadData("astree_" + id_login_database.value);
    let ret2 = await global_var.cache.loadData("astables_" + id_login_database.value);
    let ret3 = await global_var.cache.loadData("asusers_" + id_login_database.value);

    if (ret1 == null || ret2 == null || ret3 == null) {
        ajax("/db_execute", { "action": "connect_after"}, async function (a) {
            ret1 = await global_var.tree_objects.montaArvoreDados(a.tree);

            id_tree_obj.innerHTML    = ret1;
            global_var.object_tables = a.object_tables;
            global_var.object_users  = a.object_users;

            global_var.cache.saveData("astree_" + id_login_database.value, ret1);
            global_var.cache.saveData("astables_" + id_login_database.value, a.object_tables);
            global_var.cache.saveData("asusers_" + id_login_database.value, a.object_users);

        });        

    } else {
        id_tree_obj.innerHTML    = ret1;
        global_var.object_tables = ret2;
        global_var.object_users  = ret3;
    }
    id_tree_obj.index = 0;
}

function js_dbtree_show() {
    id_tree_obj.innerHTML = id_tree_obj.value;
    id_tree_obj.index     = 0;
}

function js_tree_login_saved(x) {
    d = x.split("/");
    id_login_database.selectedIndex = Array.from(id_login_database.options).findIndex(opt => opt.text === d[2]);
    id_login_username.value = d[0];
    id_login_password.value = d[1];
}


function js_show_last_sql() {
  js_window_popup('last_sql',id_menu_qtd_char.sql,true);
}

function getStatementAtCursor(text_full, offset) {
    function tokenize(text) {
        const tokens = [];
        let i = 0;

        let inString = false;
        let inLineComment = false;
        let inBlockComment = false;

        while (i < text.length) {
            const c = text[i];
            const next = text[i + 1];

            // comentários
            if (inLineComment) {
                if (c === '\n') inLineComment = false;
                i++;
                continue;
            }

            if (inBlockComment) {
                if (c === '*' && next === '/') {
                    inBlockComment = false;
                    i += 2;
                    continue;
                }
                i++;
                continue;
            }

            if (!inString && c === '-' && next === '-') {
                inLineComment = true;
                i += 2;
                continue;
            }

            if (!inString && c === '/' && next === '*') {
                inBlockComment = true;
                i += 2;
                continue;
            }

            // string
            if (c === "'") {
                if (inString && next === "'") {
                    i += 2;
                    continue;
                }
                inString = !inString;
                i++;
                continue;
            }

            if (inString) {
                i++;
                continue;
            }

            // tokens relevantes
            if (/[a-zA-Z]/.test(c)) {
                let start = i;
                while (/[a-zA-Z_]/.test(text[i])) i++;
                tokens.push({
                    type: "word",
                    value: text.slice(start, i).toUpperCase(),
                    pos: start
                });
                continue;
            }

            if (c === ';' || c === '/') {
                tokens.push({ type: "symbol", value: c, pos: i });
            }

            i++;
        }

        return tokens;
    }
    var text = text_full + "\n;";
    const tokens = tokenize(text);

    let blockLevel = 0;
    let start = 0;
    let end = text.length;

    for (let t of tokens) {
        if (t.pos > offset) break;

        if (t.type === "word") {
            if (t.value === "BEGIN" || t.value === "DECLARE") {
                if (blockLevel === 0) start = t.pos;
                blockLevel++;
            }

            if (t.value === "END") {
                blockLevel = Math.max(0, blockLevel - 1);
            }
        }

        if (t.type === "symbol" && t.value === ';') {
            if (blockLevel === 0) {
                start = t.pos + 1;
            }
        }
    }

    blockLevel = 0;

    for (let t of tokens) {
        if (t.pos < offset) continue;

        if (t.type === "word") {
            if (t.value === "BEGIN" || t.value === "DECLARE") {
                blockLevel++;
            }

            if (t.value === "END") {
                blockLevel = Math.max(0, blockLevel - 1);
            }
        }

        if (t.type === "symbol") {
            if (t.value === ';' && blockLevel === 0) {
                end = t.pos;
                break;
            }

            // suporte ao "/" isolado (SQL Developer style)
            if (t.value === '/' && blockLevel === 0) {
                end = t.pos;
                break;
            }
        }
    }

    return text.substring(start, end).trim();
}



function get_sql_editor_portion() {
    var editor = global_var.editorSQL;

    const model = editor.getModel();
    const position = editor.getPosition();
    const offset = model.getOffsetAt(position);

    return  getStatementAtCursor( global_var.editorSQL.getValue() , offset-1);
}


function get_sql_editor() {
    if ( id_div_compiler.style.display == 'flex' ) {
        return global_var.editorSQL.getValue();
    }
    
    const selection    = global_var.editorSQL.getSelection();
    const selectedText = global_var.editorSQL.getModel().getValueInRange(selection);
    let finalText      = selectedText;

    if (!selectedText) {
        finalText = get_sql_editor_portion();
    }
    return finalText;
}




function jsExportToFile(sql,type) {
    table_name = "";
    if ( type == 0 ) {
        table_name = prompt("Table Name","table_name");
    }

    id_message_box_form.style.display = "flex";
    id_message_box_text.innerHTML = "Exporting...";

    var formData = {
                action: "export_to_file", 
                type:type,
                table_name: table_name,
                sql:sql
    };

    ajax("/db_execute", formData, function (a) {
        js_global_thread_status(id_message_box_form, id_message_box_text);
    });
}


function js_clear_cache() {
    global_var.cache.clear();
    alert('Cache Cleared! The tree will be reloaded on next access.');
}
/*
    ==========================================================================================------------------------------------
    comment: Funcoes para embelezar e formatar o codigo PL/SQL, utilizando uma chamada ao servidor para processar o código e retornar uma versão formatada, que é então exibida no editor SQL.
    ==========================================================================================------------------------------------
*/


function js_format_plsql() {
    const selection    = global_var.editorSQL.getSelection();
    const selectedText = global_var.editorSQL.getModel().getValueInRange(selection);

    if ( !selectedText ) {
        alert("Select the PL/SQL code to format.");
        return;
    }

    ajax("/format_plsql", {"code": selectedText}, function (a) {
        global_var.editorSQL.executeEdits("", [
                {
                    range: selection,
                    text: a.newcode
                }
            ]);        
    });    

}
/*
    ==========================================================================================------------------------------------
    comment: Funcoes para tela de ediçao de objetos
    ==========================================================================================------------------------------------
*/

function js_editor_mode_close() {
    id_div_compiler.style.display = 'none';
    id_div_compiler_spec.style.display = 'none';
    global_var.editorSQL.setValue("select * from dual");
}

function js_editor_mode_goto() {
    if ( id_div_compiler_spec.innerText == 'body' ) {
        id_div_compiler_spec.spec      = global_var.editorSQL.getValue();
        id_div_compiler_spec.specVS    = global_var.editorSQL.saveViewState(); 
        id_div_compiler_spec.innerText = 'spec';
        global_var.editorSQL.setValue( id_div_compiler_spec.body );
        global_var.editorSQL.restoreViewState(id_div_compiler_spec.bodyVS);

    } else {
        id_div_compiler_spec.body      = global_var.editorSQL.getValue();
        id_div_compiler_spec.bodyVS    = global_var.editorSQL.saveViewState(); 
        id_div_compiler_spec.innerText = 'body';
        global_var.editorSQL.setValue( id_div_compiler_spec.spec )
        global_var.editorSQL.restoreViewState(id_div_compiler_spec.specVS);
    }
    global_var.editorSQL.focus();    
}


function js_editor_mode_open(object_name) {
    change_icon(true);
    ajax("/db_execute", { "action": "ddl", "object_name": object_name }, function (a) {
        if ( a.status_code != 0 ) {
            alert(a.status_msg);
            return;
        }

        var code = a.status_msg.split("<end_package_spec>");
        global_var.editorSQL.setValue( code[0].trim() );
        if ( code.length > 1 ) {
            id_div_compiler_spec.style.display = 'flex';
            id_div_compiler_spec.innerText     = 'body';
            id_div_compiler_spec.spec          = code[0].trim();
            id_div_compiler_spec.body          = code[1].trim();
            id_div_compiler_spec.specVS        = null;
            id_div_compiler_spec.bodyVS        = null;
        }

        id_div_compiler.style.display = 'flex';
        change_icon(false);
        id_find_object_form.style.display = "none";
    });
}


/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à execução de threads no servidor para operações longas, como o CSV Completer, 
    e para verificar o status dessas operações.
    ==========================================================================================------------------------------------
*/


function js_global_thread_status(id_logger, id_logger_text) {
    
    if (id_logger.style.display !== "flex") {
        ajax("/th_stop", {}, function (aa) {
            id_logger_text.innerHTML = aa.status_msg;
        });            
        return;
    }

    ajax("/th_status", {_: Date.now()}, function (a) {
        id_logger_text.innerHTML = a.status_msg;
        if ( a.status_code != 0  ) {
            setTimeout(() => {
                js_global_thread_status(id_logger, id_logger_text);
            }, 2000);
        }
    });
}


/*
    ==========================================================================================------------------------------------
    comment: Funções específicas do CSV Completer
    ==========================================================================================------------------------------------
*/

async function js_csv_completer_execute() {

    const input = document.getElementById("id_csv_completer_filename");

    const file = input.files[0];
    const content = await file.text();    

    const formData = new FormData();
    formData.append("action", "csv_completer");
    formData.append("file_data", content);
    formData.append("file_name", file.name);
    formData.append("sql", id_csv_completer_query.value);
    formData.append("first_line_titles", id_csv_completer_options.value);

    console.log(content);

    ajax("/db_execute", formData, function (a) {
        js_global_thread_status(id_csv_completer_form, id_csv_completer_status);
    }, null, false);
}

function js_csv_completer_form() {
    id_csv_completer_form.style.display = "flex";
}



/*
    ==========================================================================================------------------------------------
    comment: Função para abrir um template SQL salvo, permitindo ao usuário selecionar um arquivo de template e carregar seu conteúdo no editor SQL.
    ==========================================================================================-------------------------------------
*/

function js_template_save() {
    ajax("/template", { "action": "save", "old_name": id_menu_template_name.innerText, "name": id_template_name.value, "value": global_var.editorSQL.getValue() }, function (a) {
        if ( id_menu_template_name.innerText !==  id_template_name.value) {
            js_template_load();
        }
        id_menu_template_name.innerText = id_template_name.value;
        id_template_form.style.display  = "none";
        alert('Saved Sucess');
    });
}

function js_template_close() {
    if ( id_menu_template_name.innerText != "" ) {
        id_template_form.style.display = "none";
        id_menu_template_name.innerText = "";
        global_var.editorSQL.setValue("select * from dual");
    } else {
        alert("No template loaded!");
    }
}

function js_templates_open_item(x) {
    if ( confirm('Open this template in current editor?') ) {
        ajax("/template", { "action": "open", "name": x}, function (a) {
            id_template_name.value          = x;
            id_menu_template_name.innerText = x;
            global_var.editorSQL.setValue(a.code);
        });
    }
}

function js_template_load() {
    if ( id_tree_obj.index == 0 ) {
        id_tree_obj.value        = id_tree_obj.innerHTML;
    }

    ajax("/template", { "action": "load" }, function (a) {
        id_tree_obj.innerHTML    = global_var.tree_templates.montaArvoreDados(a.templates);        
        id_tree_obj.index        = 1;
    });
}


function js_template_form() {
    id_template_form.style.display = "flex";
    id_template_name.value         = id_menu_template_name.innerText;
}



/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à funcionalidade de "Find Object", que permite a
    o usuário buscar objetos no banco de dados por nome.
    ==========================================================================================------------------------------------
*/


function js_find_object_execute() {
    id_find_object_grid.innerHTML = '';
    ajax("/db_execute", { "action": "findobj", "object_name": id_find_object_name.value }, function (a) {

        global_var.grid_find_objects.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100,
            [
                { texto: 'DDL', funcao: function (item) { js_db_ddl(item.OWNER + '...' + item.OBJECT_TYPE + '...' + item.OBJECT_NAME); } },

                { texto: 'edit', funcao: function (item) { js_editor_mode_open(item.OWNER + '...' + item.OBJECT_TYPE + '...' + item.OBJECT_NAME); } }
            ]
        );
        global_var.grid_find_objects.desenharTabela();
    });
}


function js_find_object_form() {
    id_find_object_form.style.display = "flex";
}



/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à visualização de sessões ativas no banco de dados, 
    permitindo ao usuário monitorar e gerenciar as conexões.
    ==========================================================================================------------------------------------
*/

function js_view_sessions_execute() {
    id_view_sessions_grid.innerHTML = '';
    ajax("/db_execute", { "action": "view_sessions", "status": id_view_sessions_status.value }, function (a) {
        global_var.grid_view_sessions.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100
        );
        global_var.grid_view_sessions.desenharTabela();
    });
}


function js_view_sessions_form() {
    id_view_sessions_form.style.display = "flex";
}

/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas ao recurso de "Recall SQL", que permite ao usuário 
    visualizar e gerenciar consultas SQL previamente executadas.
    ==========================================================================================------------------------------------
*/

function js_recall_sql_execute() {
    id_recall_sql_grid.innerHTML = '';
    ajax("/config_recall", { "database": id_recall_sql_database.value, "text": id_recall_sql_text.value }, function (a) {
        global_var.grid_recall_sql.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100,
            [
                { texto: 'copy', funcao: function (item) { copyToClip(item.SQL); } }
            ]            
        );
        global_var.grid_recall_sql.columns_types[2] = 'PRE';
        global_var.grid_recall_sql.desenharTabela();
    });
}

function js_recall_sql_form() {
    id_recall_sql_form.style.display = "flex";
}



/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à integração com IA, permitindo ao usuário gerar consultas SQL a partir de descrições 
    em linguagem natural ou obter explicações sobre o funcionamento de consultas.
    ==========================================================================================------------------------------------
*/

async function js_ia_chat_api(msg) {
    const modelo = "gemini-flash-latest";
    const API_KEY = "AIzaSyAUbgnZiV2fW-e50ql_P9CCBvmyXz03-Kc";

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent?key=${API_KEY}`;

    const payload = {
        contents: [
            {
                parts: [{ text: msg }]
            }
        ]
    };

    try {
        const resp = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await resp.json();

        const texto = data?.candidates?.[0]?.content?.parts?.[0]?.text;

        return texto || "Sem resposta";

    } catch (err) {
        console.error("Erro:", err);
        return "Erro ao chamar API";
    }
}


function js_ia_form() {
    window.open("/ia", name, "width=800,height=400,scrollbars=yes,resizable=yes");
}

function js_ia_chat() {
    id_chat_enviar.style.backgroundColor = 'gray';
    id_chat_enviar.disabled = true;
    id_chat_enviar.innerHTML = "Sending...";

    js_ia_chat_api( id_chat_dados.value.replace("@sql", "[" + window.opener.get_sql_editor() + "]" ) ).then((message) => {
        id_chat.innerHTML = id_chat.innerHTML + "<pre>" + message + "</pre><hr>";
        id_chat_enviar.style.backgroundColor = '';
        id_chat_enviar.disabled = false;
        id_chat_enviar.innerHTML = "Send";
    });
}

/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à configuração de preferências do usuário, 
    como diretórios de templates e arquivos de configuração,
    ==========================================================================================------------------------------------
*/

function js_preferences_load_tns() {
    ajax("/config_tnsnames", {}, function (a) { 
        js_window_popup("TNS Names", a.tnsnames);
    });
}

function js_preferences_form() {
    ajax("/config_get", {}, function (a) {
        id_preferences_oh.value = a.oracle_home;
        id_preferences_tns.value = a.tns;
        id_preferences_tns_saved.value = a.tnsSaved;
        id_preferences_form.style.display = "flex";
    });
}

function js_preferences_save() {
    r = {
        "tns": id_preferences_tns.value,
        "tnsSaved": id_preferences_tns_saved.value
    };

    ajax("/config_save", r, function (a) {
        alert( a.status_msg );
        id_preferences_form.style.display = "none";
        global_var.config_loaded          = false;
    });
}

/*
    ==========================================================================================------------------------------------
    comment: Login e Logoff
    ==========================================================================================------------------------------------
*/

function js_logoff_form() {
    ajax("/db_execute", { "action": "logoff" }, function (a) {
        change_icon();
    });    
}


function js_login_change_password() {
    ajax("/db_execute", { "action": "change_password_get_user", "alias": id_login_database.options[id_login_database.selectedIndex].innerText }, async function (a) {
        if (a.status_msg.startsWith("ERROR")) {
            alert(a.status_msg);
        } else {
            if ( confirm("Change password for user " + a.db_user + "@" + id_login_database.options[id_login_database.selectedIndex].innerText + "?")  ) {
                ajax("/db_execute", { "action": "change_password", "db_tns": a.db_tns, "db_user": a.db_user, "db_password": id_login_password.value }, async function (a) {
                    alert(a.status_msg);
                });   
            }
        }
    });   
}

function js_login_connect() {
    ajax("/db_execute", { "action": "connect", "usr": id_login_username.value, "pwd": id_login_password.value, "tns": id_login_database.value, "direct": id_login_direct.value }, async function (a) {
        change_icon(false);

        if ( a.status_code == 0 ) {
            await js_monta_tree();
            id_login_form.style.display = "none";    
        } else {
            alert( a.status_msg );
        }
    });
}


function js_login_form() {
    ajax("/config_get", {}, function (a) {
        id_login_form.style.display = "flex";

        if ( global_var.config_loaded == false ) {
            id_login_list_tns_saved.innerHTML = "";

            var root = '';
            var dados = '';
            var x = a.tnsSaved.split("\n");
            for (var i = 0; i < x.length; i++) {
                if (x[i].indexOf(">") >= 0) {
                    root = (x[i].split(">")[1]).trim();
                }
                if (x[i].indexOf("|") >= 0) {
                    var inf = x[i].split("|");
                    dados = dados + root + "|" + inf[0] + "/" + inf[1] + "/" + inf[2] + "\n";
                }
            }
            id_login_list_tns_saved.innerHTML = global_var.tree_login.montaArvoreDados(dados);
            id_login_database.innerHTML = "";
            var x = a.tns.split("\n");
            for (var i = 0; i < x.length; i++) {                
                if ( x[i].includes("##") == false && x[i].indexOf("|") >= 0) {
                    nn = (x[i].split("|")[0]).trim();
                    vv = (x[i].split("|")[1]).trim();
                    id_login_database.innerHTML += "<option value=\"" + vv + "\">" + nn + "</option>";
                }
            }
            global_var.config_loaded = true;
        }

    });
}


/*
    ==========================================================================================------------------------------------
    comment: Funções de banco de dados
    ==========================================================================================------------------------------------
*/

function js_db_execute_proc( obj ) {
    ajax("/db_execute", { "action": "test_procedure", "object_name": obj }, function (a) {
        js_window_popup("test proc", a.status_msg);
    });
}

function js_db_status(in_transaction = null, in_running = null, is_connected = null) {
    if (in_transaction != null) {
        id_menu_commit.disabled = !in_transaction;
        id_menu_rollback.disabled = !in_transaction;
    }
}


function js_db_grid_editrow(row, columns, columns_types) {
    const container = document.getElementById('id_edit_row_grid_content');
    container.innerHTML = '';
    container.row = row;
    id_edit_row_bt_save.style.display = 'none';

    columns.forEach((c, idx) => {
        if (idx === 0) return;

        if (c == "ROWID") {
            container.rowid = row.cells[idx].value;
            id_edit_row_bt_save.style.display = '';
        } else {
            const tr  = document.createElement('tr');
            const td1 = document.createElement('td');
            td1.textContent = c;

            const td2   = document.createElement('td');
            const is_textarea = columns_types[idx - 1].includes("LOB") || String(row.cells[idx].value).includes("\n");

            const input = document.createElement(is_textarea ? 'textarea' : 'input');
            input.type = 'text';
            input.id = `id_row_edit_field_${c}`;
            input.value = row.cells[idx].value;
            input.spellcheck = false;
            td2.appendChild(input);

            tr.appendChild(td1);
            tr.appendChild(td2);
            container.appendChild(tr);
        }
    });

    document.getElementById('id_edit_row_grid_form').style.display = 'flex';
}

function js_db_grid_editrow_save() {
    const itens = {};
    global_var.grid_query.columns.forEach((v, idx) => {
        if (idx == 0 || v == 'ROWID') return;
        itens[v] = document.getElementById('id_row_edit_field_' + v).value;
        itens['@' + v] = global_var.grid_query.columns_types[idx - 1];
    });

    params = {
        "action": "save_row_grid",
        "itens": JSON.stringify(itens),
        "rowid": id_edit_row_grid_content.rowid,
        "sql": global_var.grid_query.sql
    };

    ajax("/db_execute", params, function (a) {
        alert(a.status_msg);
        if ( a.status_code == 0 ) {
            js_db_status(in_transaction = true);
            
            global_var.grid_query.columns.forEach((v, idx) => {
                if (idx == 0 || v == 'ROWID') return;
                td = id_edit_row_grid_content.row.cells[idx];
                if ( global_var.grid_query.columns_types[idx - 1].includes("LOB") == false ) {
                    td.innerText = document.getElementById('id_row_edit_field_' + v).value;
                }
                td.value = document.getElementById('id_row_edit_field_' + v).value;
            });            
        }
    });

}

function js_db_ddl(object_name) {
    change_icon(true);
    ajax("/db_execute", { "action": "ddl", "object_name": object_name }, function (a) {
        if ( a.status_code != 0 ) {
            alert(a.status_msg);
            return;
        }
        js_window_popup("DDL: " + object_name, a.status_msg);
        change_icon(false);
    });
}






function js_db_execute() {
    id_grid_dados.innerHTML    = '';
    id_menu_qtd_char.innerHTML = '';
    sql   = get_sql_editor();

    if ( sql.length < 3 ) {
        alert('No SQL Avalilable!');
        return;
    }
    
    change_icon(true);
    global_var.tm_elapsed.start();
    id_menu_qtd_char.innerHTML = "<a href=# onclick=js_show_last_sql()>" + sql.length + " chars </a>";
    
    ajax("/db_execute", { "action": "execute", "sql": sql }, function (a) {
        global_var.tm_elapsed.stop();
        if ( a.status_code != 0 ) {
            alert(a.status_msg);
            change_icon(false);
            return;
        }

        global_var.dbms_output            = a.dbms;
        id_dbms_output.style.display      = (a.sql_type == 1) ? 'none'  : 'block';
        id_grid_dados.style.display       = (a.sql_type == 1) ? 'block' : 'none';
        id_grid_dados_pager.style.display = (a.sql_type == 1) ? 'block' : 'none';

        if (a.sql_type == 1) {
            global_var.grid_query.setContent(a.data, a.columns, a.columns_types, 50, [], sql);
            global_var.grid_query.desenharTabela();
        } else {
            id_dbms_output.innerHTML = "<pre>" + a.status_msg + "<br>" + a.dbms + "</pre>"; 
            js_db_status(in_transaction = true);
        }
        change_icon(false);
        id_menu_qtd_char.sql  = `<h2>dbms output:</h2><br>${ global_var.dbms_output } <br><h2>sql:</h2><br>${ sql }`;
    }, function (error) {
        global_var.tm_elapsed.stop();
        alert(error);
        change_icon(false);
    });
}


function js_db_stop() {
    ajax("/db_execute", { "action": "stop", }, function (a) {
        change_icon(false);
    }, function (error) {
        change_icon(false);
    });
}


function js_db_explain() {
    ajax("/db_execute", { "action": "explain", "sql": get_sql_editor() }, function (a) {
        if ( a.status_code != 0 ) {
            alert(a.status_msg);
            return;
        }
        js_window_popup("EXPLAIN", a.explain);
    });
}

function js_db_completation(type_filter, type_object) {
    return new Promise((resolve, reject) => {
        ajax(
            "/db_execute",
            {
                action: "tab_columns",
                "type_filter": type_filter,
                "type_object": type_object
            },
            function (resp) {     // sucesso
                resolve(resp.data);
            },
            function (err) {      // erro
                reject(err);
            }
        );
    });
}


function js_db_transaction(action) {
    ajax("/db_execute", { "action": "action", action }, function (a) { 
        js_db_status(in_transaction = false);
    });
}


function js_db_describe() {
    obj = get_sql_editor();
    if (global_var.object_tables.includes(obj.toUpperCase())) {
        ajax("/db_execute", { "action": "describe", "object_name": obj },
            function (a) {
                js_window_popup("DESCRIBE: " + obj, a.describe, true);
            }
        );
    } else {
        alert("Table Not Found!");
    }

}

function js_db_fetch50(grid) {
    ajax("/db_execute", { "action": "fetch", }, function (a) {
        if (a.data.length > 0) {
            grid.dados = grid.dados.concat(a.data);
            grid.paginaAtual++; 
            grid.desenharTabela();
        } else {
            grid.btnNext.disabled = true;
        }
    });
}

function js_db_fetch(append = false) {
    if (append == false) {
        change_icon(true);
        id_message_box_form.style.display = "flex";
    }
    else {
        if (id_message_box_form.style.display != "flex") {
            change_icon(false);
            global_var.grid_query.desenharPaginacao();
            return
        }
    }

    ajax("/db_execute", { "action": "fetch", }, function (a) {
        if (a.data.length > 0) {
            global_var.grid_query.dados = global_var.grid_query.dados.concat(a.data);
            id_message_box_text.innerHTML = global_var.grid_query.dados.length + " records fetched.";
            js_db_fetch(true);
        } else {
            change_icon(false);
            id_message_box_form.style.display = "none";
            global_var.grid_query.desenharPaginacao();
        }
    }, function (error) {
        change_icon(false);
    });
}





/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à manipulação da janela do navegador, como abertura de popups, configuração de eventos 
    e integração com o editor Monaco.
    ==========================================================================================------------------------------------
*/



function js_window_start() {
    global_var = {
        object_tables: [],
        object_users: [],
        session_id: generate_session_id(),
        tm_elapsed: new TTimer(),
        grid_query: new TGrid("id_grid_dados", { "fetch": true, "export": true, "edit": true }),
        grid_find_objects: new TGrid("id_find_object_grid"),
        grid_view_sessions: new TGrid("id_view_sessions_grid"),
        grid_recall_sql: new TGrid("id_recall_sql_grid"),
        tree_login: new TreeView(),
        tree_objects: new TreeView(),
        tree_templates: new TreeView(),
        dbms_output: "",
        config_loaded: false,
        cache: new LocalDB()
    };

    global_var.grid_query.fetch_on_next_button = true;

    global_var.tree_objects.endNodeClick = "js_db_ddl";
    global_var.tree_objects.endNodeParamClick = "nodeValues[3]";

    global_var.tree_login.endNodeClick = "js_tree_login_saved";
    global_var.tree_login.endNodeText = "nodeValue.split('/')[0] + '@' + nodeValue.split('/')[2]";

    global_var.tree_templates.endNodeClick      = "js_templates_open_item";
    global_var.tree_templates.endNodeParamClick = "nodeValues[3].replaceAll('...','|')";
    global_var.tree_templates.endNodeText       = "nodeValue.split('|').at(-1)";



    const div_tooltip = document.createElement("div");
    div_tooltip.id    = "id_tooltip";
    document.body.appendChild(div_tooltip);

    if (window.location.href.indexOf("?tab") >= 0) {
        id_login_database.innerHTML = window.opener.id_login_database.innerHTML;
        id_login_direct.innerHTML = window.opener.id_login_direct.innerHTML;
        id_login_username.value = window.opener.id_login_username.value;
        id_login_password.value = window.opener.id_login_password.value;
        id_login_database.value = window.opener.id_login_database.value;
        id_login_direct.value = window.opener.id_login_direct.value;
        js_login_connect();
    }
}


function js_window_closed() {
    window.addEventListener("beforeunload", function (e) {
        e.preventDefault();
        e.returnValue = "";
    });
}



function js_window_popup(name, content, html = false) {
    page = `<style>
                html,
                body {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    background: #f7f7f8;
                    color: #1f1f1f;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 12px;
                    padding: 10px;
                    border-left: 1px solid red;
                }

                table {
                    border-collapse: collapse;
                    font-size: 12px;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid black;
                    padding: 4px 8px;
                    text-align: left;
                }
                th {
                    background-color: #f0f0f0;
                }
        </style>    
        <body>
           <pre></pre>
        </body>
    `;

    x = window.open("", name, "width=800,height=400,scrollbars=yes,resizable=yes");
    x.document.body.innerHTML = page;

    if ( name == 'VIEW CELL') {
        var str = content;
        try {
            const obj = JSON.parse(str);
            content =  JSON.stringify(obj, null, 4);

        } catch (e) {
        }
    }

    if (html) {
        x.document.body.querySelector("pre").innerHTML = content;
    } else {
        x.document.body.querySelector("pre").textContent = content;
    }
    return x;
}



function js_window_splitters() {
    const vsplit = document.getElementById("vsplit");
    const sidebar = document.querySelector(".sidebar");

    vsplit.addEventListener("mousedown", () => {
        document.onmousemove = evt => {
            sidebar.style.width = evt.clientX + "px";
        };
        document.onmouseup = () => (document.onmousemove = null);
    });

    const hsplit = document.getElementById("hsplit");
    const editorContainer = document.getElementById("editor-container");

    hsplit.addEventListener("mousedown", e => {
        const startY = e.clientY;
        const startHeight = editorContainer.offsetHeight;

        document.onmousemove = evt => {
            editorContainer.style.flex = "0 0 auto";
            editorContainer.style.height = (startHeight + (evt.clientY - startY)) + "px";
            if (global_var.editorSQL) global_var.editorSQL.layout(); // Atualiza Monaco
        };
        document.onmouseup = () => (document.onmousemove = null);
    });
}


function js_window_editor_monaco(p_theme="vs-dark") {
    require.config({
        paths: { vs: "https://unpkg.com/monaco-editor@0.55.1/min/vs" }
    });

    require(["vs/editor/editor.main"], function () {

        monaco.languages.registerCompletionItemProvider('sql', {
            triggerCharacters: ['.'],
            async provideCompletionItems(model, position) {
                const textUntilPosition = model.getValueInRange({
                    startLineNumber: position.lineNumber,
                    startColumn: 1,
                    endLineNumber: position.lineNumber,
                    endColumn: position.column
                });

                const match = textUntilPosition.match(/(\w+)\.$/);
                const word_select = match ? match[1] : null;


                if (!word_select) return { suggestions: [] };

                let word_to_filter = "";
                let in_list_table = global_var.object_tables.includes(word_select.toUpperCase());
                let in_list_users = global_var.object_users.includes(word_select.toUpperCase());

                if (  in_list_table  || in_list_users ) {
                    word_to_filter = word_select;
                } else {
                    const fullText = model.getValue();
                    x = fullText.toUpperCase().replace(/[;,\n\t.*]| SELECT /g, ' ');
                    while (x.indexOf('  ') > 0) {
                        x = x.replaceAll('  ', ' ')
                    }
                    info_a = x.split(' ');

                    for (let i = 0; i < info_a.length; i++) {
                        const info = info_a[i];

                        if (word_select.toUpperCase() === info && global_var.object_tables.includes(info_a[i - 1])) {
                            in_list_table = true;
                            word_to_filter = info_a[i - 1];
                            break;
                        }
                    }
                }
                if (word_to_filter === "") return { suggestions: [] };

                const columns = await js_db_completation(word_to_filter, in_list_table ? "TABLE" : "USER");

                const suggestions = (columns || []).map(col => {

                    const n = String(col.N ?? "");
                    const o = String(col.O ?? "");
                    const i = String(col.I ?? "");

                    return {
                        label: {
                            label: n.padEnd(40, " "),
                            description: o,
                        },

                        sortText: i,

                        detail: in_list_table
                            ? "Column"
                            : "Object",

                        documentation: o,

                        kind: monaco.languages.CompletionItemKind.Variable,

                        insertText:
                            n + (
                                in_list_table
                                    ? ""
                                    : " " + gerar_alias(n)
                            )
                    };
                });

                return { suggestions };
            }
        });


        editor = monaco.editor.create(
            document.getElementById("editor-container"),
            {
                value: "SELECT * FROM cmf",
                language: "sql",
                theme: p_theme,
                automaticLayout: true,
                fontSize: 12,
                minimap: { enabled: true }
            }
        );

        editor.addAction({
            id: "Recall Query",
            label: "Recall Query",
            keybindings: [ monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyE ],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_recall_sql_form()
        }); 

        editor.addAction({
            id: "Execute Query",
            label: "Execute Query",
            keybindings: [ monaco.KeyCode.F8, monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter ],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_db_execute()
        });     

        editor.addAction({
            id: "Describe Table",
            label: "Describe Table",
            keybindings: [],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_db_describe()
        });

        editor.addAction({
            id: "Execute/Test Procedure",
            label: "Execute/Test Procedure",
            keybindings: [],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_db_execute_proc( get_sql_editor() )
        });        


        editor.addAction({
            id: "Explain Query",
            label: "Explain Query",
            keybindings: [ monaco.KeyCode.F5 ],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_db_explain()
        });    

        editor.addAction({
            id: "Format PlSql",
            label: "Format PlSql",
            keybindings: [ ],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_format_plsql()
        });          
        
        editor.addAction({
            id: "IA Assistant",
            label: "IA Assistant",
            keybindings: [],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,
            run: () => js_ia_form()
        });    
        
        

        global_var.editorSQL = editor;
    });
}


function js_window_fileopen() {
    const fileInput = document.getElementById('fileInput');
    fileInput.value = '';
    fileInput.click();

    fileInput.onchange = (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            global_var.editorSQL.setValue(content);
        };
        reader.readAsText(file);
    };
}
