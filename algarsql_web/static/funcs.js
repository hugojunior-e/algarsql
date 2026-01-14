
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
        // Garante objetos Date
        const d1 = this.dt_inicio;
        const d2 = this.dt_fim == null ? new Date() : this.dt_fim;

        // Diferença em milissegundos
        let diffMs = Math.abs(d2 - d1);

        const horas = Math.floor(diffMs / (1000 * 60 * 60));
        diffMs %= (1000 * 60 * 60);

        const minutos = Math.floor(diffMs / (1000 * 60));
        diffMs %= (1000 * 60);

        const segundos = Math.floor(diffMs / 1000);
        const milissegundos = diffMs % 1000;

        // Formatação com zero à esquerda
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
// --------------------------------------------------------------------------
// -- TGrid: Componente de grade de dados com paginação --- IGNORE ---
// --------------------------------------------------------------------------

class TGrid {
    constructor(idTable, options = { "fetch": false, "edit": false, "export": false }) {
        this.idTable = idTable;
        this.options = options;
    }


    setContent(dados, columns, columns_types, limit_per_page = 5, actions = [], sql = "") {
        this.columns = ["#"].concat(columns);  // adiciona ROWNUM
        this.columns_types = columns_types;
        this.colunasSemRownum = columns;       // mantém só as columns dos dados
        this.dados = dados;                    // agora é lista de dict
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


    desenharTabela() {
        this.tabela.innerHTML = "";

        // Cabeçalho
        const thead = this.tabela.createTHead();
        const headerRow = thead.insertRow();
        this.columns.forEach(c => {
            const th = document.createElement("th");
            th.textContent = c;
            headerRow.appendChild(th);
        });
        this.headerRow = headerRow;


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

            // ROWNUM botão
            const tdRownum = tr.insertCell();
            const rownum = inicio + idx + 1;
            tdRownum.innerHTML = rownum;
            if (this.options.edit) {
                tdRownum.style.cursor = 'pointer';
                tdRownum.onclick = () => js_db_edit_row(tr, this.columns, this.columns_types);
            }

            // Cria células a partir das chaves especificadas em colunasSemRownum
            this.colunasSemRownum.forEach((col, idx_td) => {
                const td = tr.insertCell();

                td.textContent = linha[col] ?? "";
                td.value = linha[col] ?? "";

                if (this.columns_types[idx_td].includes("LOB") && td.value !== "") {
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

        const btnPrev = document.createElement("button");
        btnPrev.textContent = "Prior";
        btnPrev.disabled = this.paginaAtual === 1;
        btnPrev.onclick = () => { this.paginaAtual--; this.desenharTabela(); };
        this.pager.appendChild(btnPrev);

        const info = document.createElement("span");
        info.textContent = ` Page ${this.paginaAtual} / ${this.totalPaginas} `;
        this.pager.appendChild(info);

        const btnNext = document.createElement("button");
        btnNext.textContent = "Next";
        btnNext.disabled = this.paginaAtual === this.totalPaginas;
        btnNext.onclick = () => { this.paginaAtual++; this.desenharTabela(); };
        this.pager.appendChild(btnNext);

        if (this.options.export) {
            const btnExportInsert = document.createElement("button");
            btnExportInsert.textContent = "insert";
            btnExportInsert.onclick = () => { jsExportToFile(this.sql,0); };
            this.pager.appendChild(btnExportInsert);

            const btnExportCsv = document.createElement("button");
            btnExportCsv.textContent = "csv";
            btnExportCsv.onclick = () => { jsExportToFile(this.sql,1); };
            this.pager.appendChild(btnExportCsv);
        }

        if (this.options.fetch) {
            const btnFetch = document.createElement("button");
            btnFetch.textContent = "🢃";
            btnFetch.onclick = () => { js_db_fetch(); };
            this.pager.appendChild(btnFetch);
        }
    }
}


// --------------------------------------------------------------------------
// -- ajax
// --------------------------------------------------------------------------

function ajax(url, dataBody, jsAction, jsError = null) {
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(dataBody)
    })
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



// --------------------------------------------------------------------------
// -- 
// --------------------------------------------------------------------------


function parseDataBR(str) {
    const [data, hora] = str.split(" ");
    const [dia, mes, ano] = data.split("/").map(Number);
    const [h, m, s] = hora ? hora.split(":").map(Number) : [0, 0, 0];

    return new Date(ano, mes - 1, dia, h, m, s);
}


function generate_session_id() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

function change_icon(running) {
    document.title = (running ? "🔴" : "🔵") + " " + document.caption;
}


function executarEmBackground(fn) {
    return new Promise(resolve => {
        setTimeout(() => resolve(fn()), 0);
    });
}

function pausa() {
    return new Promise(resolve => setTimeout(resolve, 0));
}


async function js_monta_tree(data) {
    ret = window.localStorage.getItem("tree_" + id_login_database.value);
    if (ret == null) {
        await pausa();
        ret = await executarEmBackground(() => window.tree_objects.montaArvoreDados(data));
        window.localStorage.setItem("tree_" + id_login_database.value, ret);
    }
    id_tree_obj.innerHTML = ret;
}



function js_tree_login_saved(x) {
    d = x.split("/");
    id_login_database.selectedIndex = Array.from(id_login_database.options).findIndex(opt => opt.text === d[2]);
    id_login_username.value = d[0];
    id_login_password.value = d[1];
}


function get_sql_editor() {
    const selection = window.editorSQL.getSelection();
    const selectedText = window.editorSQL.getModel().getValueInRange(selection);
    let finalText = selectedText;

    if (!selectedText) {
        finalText = window.editorSQL.getValue();
    }
    return finalText;
}


function jsExportToFile(sql,type) {
    change_icon(true);
    table_name = "";
    if ( type == 0 ) {
        table_name = prompt("Table Name","table_name");
    }
    ajax("/db_execute", { "session_id": window.session_id, "action": "export_to_file", "type":type, "table_name": table_name, "sql": sql }, function (a) {
        alert( a.status_msg );
        change_icon(false);
    }, function (error) {
        alert(error);
        change_icon(false);
    });
}

//--------------------------------------------------------------------------
//-- Funções específicas do AlgarSQL Web --- IGNORE ---
//--------------------------------------------------------------------------

function js_find_object_form() {
    id_find_object_form.style.display = "flex";
}

function js_find_object_click() {
    id_find_object_grid.innerHTML = '';
    ajax("/db_execute", { "session_id": window.session_id, "action": "findobj", "object_name": id_find_object_name.value }, function (a) {

        window.grid_find_objects.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100,
            [{ texto: 'DDL', funcao: function (item) { js_db_ddl(item.OWNER + '...' + item.OBJECT_TYPE + '...' + item.OBJECT_NAME); } }]
        );
        window.grid_find_objects.desenharTabela();
    });
}



function js_view_sessions_form() {
    id_view_sessions_form.style.display = "flex";
}

function js_view_sessions_click() {
    id_view_sessions_grid.innerHTML = '';
    ajax("/db_execute", { "session_id": window.session_id, "action": "view_sessions", "status": id_view_sessions_status.value }, function (a) {
        window.grid_view_sessions.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100
        );
        window.grid_view_sessions.desenharTabela();
    });
}


function js_recall_sql_form() {
    id_recall_sql_form.style.display = "flex";
}


function js_recall_sql_click() {
    id_recall_sql_grid.innerHTML = '';
    ajax("/db_execute", { "action": "recall_sql", "database": id_recall_sql_database.value, "text": id_recall_sql_text.value }, function (a) {
        window.grid_recall_sql.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100
        );
        window.grid_recall_sql.desenharTabela();
    });
}

function js_preferences_form() {
    ajax("/get_config", {}, function (a) {
        id_preferences_oh.value = a.OracleInstantClientDir;
        id_preferences_td.value = a.template_dir;
        id_preferences_od.value = a.output_dir;
        id_preferences_tns.value = a.tns;
        id_preferences_tns_saved.value = a.tnsSaved;
        id_preferences_form.style.display = "flex";
    });
}

function js_preferences_save() {
    r = {
        "OracleInstantClientDir": id_preferences_oh.value,
        "template_dir": id_preferences_td.value,
        "output_dir": id_preferences_od.value,
        "tns": id_preferences_tns.value,
        "tnsSaved": id_preferences_tns_saved.value
    };

    ajax("/save_config", r, function (a) {
        alert( a.status_msg );
        id_preferences_form.style.display = "none";
        window.config_loaded              = false;
    });
}


function js_login_form() {
    ajax("/get_config", {}, function (a) {
        id_login_form.style.display = "flex";

        if ( window.config_loaded == false ) {
            id_list_tns_saved.innerHTML = "";

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
            id_list_tns_saved.innerHTML = window.tree_login.montaArvoreDados(dados);
            id_login_database.innerHTML = "";
            var x = a.tns.split("\n");
            for (var i = 0; i < x.length; i++) {
                if (x[i].indexOf("|") >= 0) {
                    nn = (x[i].split("|")[0]).trim();
                    vv = (x[i].split("|")[1]).trim();
                    id_login_database.innerHTML += "<option value=\"" + vv + "\">" + nn + "</option>";
                }
            }
            window.config_loaded = true;
        }

    });


}


//--------------------------------------------------------------------------
//-- Funções de banco de dados --- IGNORE ---
//--------------------------------------------------------------------------
function js_db_status(in_transaction = null, in_running = null, is_connected = null) {
    if (in_transaction != null) {
        id_menu_commit.disabled = !in_transaction;
        id_menu_rollback.disabled = !in_transaction;
    }
}

function js_db_dbms() {
    js_window_popup("DBMS", window.dbms_output);
}

function js_db_edit_row(row, columns, columns_types) {
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
            const div = document.createElement('div');
            div.className = 'pref-row';

            const label = document.createElement('label');
            label.textContent = c;

            const input = document.createElement(columns_types[idx - 1].includes("LOB") ? 'textarea' : 'input');
            input.type = 'text';
            input.id = `id_row_edit_field_${c}`;
            input.value = row.cells[idx].value;
            input.spellcheck = false;

            div.appendChild(label);
            div.appendChild(input);

            container.appendChild(div);
        }
    });

    document.getElementById('id_edit_row_grid_form').style.display = 'flex';
}

function js_db_edit_row_save() {
    const itens = {};
    window.grid_query.columns.forEach((v, idx) => {
        if (idx == 0 || v == 'ROWID') return;
        itens[v] = document.getElementById('id_row_edit_field_' + v).value;
        itens['@' + v] = window.grid_query.columns_types[idx - 1];
    });

    params = {
        "session_id": window.session_id,
        "action": "save_row_grid",
        "itens": JSON.stringify(itens),
        "rowid": id_edit_row_grid_content.rowid,
        "sql": window.grid_query.sql
    };

    ajax("/db_execute", params, function (a) {
        alert(a.status_msg);
        if ( a.status_code == 0 ) {
            js_db_status(in_transaction = true);
            
            window.grid_query.columns.forEach((v, idx) => {
                if (idx == 0 || v == 'ROWID') return;
                td = id_edit_row_grid_content.row.cells[idx];
                if ( window.grid_query.columns_types[idx - 1].includes("LOB") == false ) {
                    td.innerText = document.getElementById('id_row_edit_field_' + v).value;
                }
                td.value = document.getElementById('id_row_edit_field_' + v).value;
            });            
        }
    });

}

function js_db_ddl(object_name) {
    change_icon(true);
    ajax("/db_execute", { "session_id": window.session_id, "action": "ddl", "object_name": object_name }, function (a) {
        if ( a.status_code != 0 ) {
            alert(a.status_msg);
            return;
        }
        js_window_popup("DDL: " + object_name, a.status_msg);
        change_icon(false);
    });
}





function js_db_connect() {
    ajax("/db_execute", { "session_id": window.session_id, "action": "connect", "usr": id_login_username.value, "pwd": id_login_password.value, "tns": id_login_database.value, "direct": id_login_direct.value }, async function (a) {
        change_icon(false);

        if ( a.status_code == 0 ) {
            document.caption = id_login_username.value + "@" + id_login_database.options[id_login_database.selectedIndex].innerText;
            js_monta_tree(a.tree);
            alert( a.status_msg );
            window.object_tables = a.object_tables;
            window.object_users  = a.object_users;
            id_login_form.style.display = "none";
        } else {
            alert( a.status_msg );
        }
    });
}


function js_db_execute() {
    
    change_icon(true);
    id_grid_dados.innerHTML = '';
    sql   = get_sql_editor();
    
    window.tm_elapsed.start();

    ajax("/db_execute", { "session_id": window.session_id, "action": "execute", "sql": sql }, function (a) {
        window.tm_elapsed.stop();
        if ( a.status_code != 0 ) {
            alert(a.status_msg);
            change_icon(false);
            return;
        }

        window.dbms_output = a.dbms;

        if (a.sql_type == 1) {
            window.grid_query.setContent(a.data, a.columns, a.columns_types, 50, [], sql);
            window.grid_query.desenharTabela();
        } else {
            alert(a.status_msg);
            js_db_status(in_transaction = true);
        }
        change_icon(false);
    }, function (error) {
        window.tm_elapsed.stop();
        alert(error);
        change_icon(false);
    });
}


function js_db_stop() {
    ajax("/db_execute", { "session_id": window.session_id, "action": "stop", }, function (a) {
        change_icon(false);
    }, function (error) {
        change_icon(false);
    });
}


function js_db_explain() {
    ajax("/db_execute", { "session_id": window.session_id, "action": "explain", "sql": get_sql_editor() }, function (a) {
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
                session_id: window.session_id,
                action: "tab_columns",
                "type_filter": type_filter,
                "type_object": type_object
            },
            function (resp) {     // sucesso
                resolve(resp);
            },
            function (err) {      // erro
                reject(err);
            }
        );
    });
}


function js_db_transaction(action) {
    ajax("/db_execute", { "session_id": window.session_id, "action": "action", action }, function (a) { 
        js_db_status(in_transaction = false);
    });
}


function js_db_describe(object_name) {
    ajax("/db_execute", { "session_id": window.session_id, "action": "describe", "object_name": object_name },
        function (a) {
            js_window_popup("DESCRIBE: " + object_name, a.describe, true);
        }
    );
}


function js_db_fetch(append = false) {
    if (append == false) {
        change_icon(true);
        id_message_box_form.style.display = "flex";
    }
    else {
        if (id_message_box_form.style.display != "flex") {
            change_icon(false);
            window.grid_query.desenharPaginacao();
            return
        }
    }

    ajax("/db_execute", { "session_id": window.session_id, "action": "fetch", }, function (a) {
        if (a.data.length > 0) {
            window.grid_query.dados = window.grid_query.dados.concat(a.data);
            id_message_box_text.innerHTML = window.grid_query.dados.length + " records fetched.";
            js_db_fetch(true);
        } else {
            change_icon(false);
            id_message_box_form.style.display = "none";
            window.grid_query.desenharPaginacao();
        }
    }, function (error) {
        change_icon(false);
    });
}





//--------------------------------------------------------------------------
//-- Funções de janela --- IGNORE ---
//--------------------------------------------------------------------------



function js_window_start() {
    window.object_tables = [];
    window.object_users  = [];
    window.session_id = generate_session_id();

    window.tm_elapsed = new TTimer();

    window.grid_query = new TGrid("id_grid_dados", options = { "fetch": true, "export": true, "edit": true });
    window.grid_find_objects = new TGrid("id_find_object_grid");
    window.grid_view_sessions = new TGrid("id_view_sessions_grid");
    window.grid_recall_sql = new TGrid("id_recall_sql_grid");
    window.tree_login = new TreeView();
    window.tree_objects = new TreeView();
    window.file_name = "";
    window.config_loaded = false;

    window.tree_objects.endNodeClick = "js_db_ddl";
    window.tree_objects.endNodeParamClick = "nodeValues[3]";

    window.tree_login.endNodeClick = "js_tree_login_saved";
    window.tree_login.endNodeText = "nodeValue.split('/')[0] + '@' + nodeValue.split('/')[2]";


    if (window.location.href.indexOf("?tab") >= 0) {
        id_login_database.innerHTML = window.opener.id_login_database.innerHTML;
        id_login_direct.innerHTML = window.opener.id_login_direct.innerHTML;
        id_login_username.value = window.opener.id_login_username.value;
        id_login_password.value = window.opener.id_login_password.value;
        id_login_database.value = window.opener.id_login_database.value;
        id_login_direct.value = window.opener.id_login_direct.value;
        js_db_connect();
    }
}


function js_window_closed() {
    window.addEventListener("beforeunload", function (e) {
        e.preventDefault();
        e.returnValue = "";
    });
}


function js_window_popup(name, content, html = false) {
    x = window.open("", name, "width=800,height=400,scrollbars=yes,resizable=yes");
    x.document.body.innerHTML = "<pre></pre>";

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
            if (window.editorSQL) window.editorSQL.layout(); // Atualiza Monaco
        };
        document.onmouseup = () => (document.onmousemove = null);
    });
}


function js_window_monaco() {
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
                let in_list_table = window.object_tables.includes(word_select.toUpperCase());
                let in_list_users = window.object_users.includes(word_select.toUpperCase());

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

                        if (word_select.toUpperCase() === info && window.object_tables.includes(info_a[i - 1])) {
                            in_list_table = true;
                            word_to_filter = info_a[i - 1];
                            break;
                        }
                    }
                }
                if (word_to_filter === "") return { suggestions: [] };

                const columns = await js_db_completation(word_to_filter, in_list_table ? "TABLE" : "USER");

                const suggestions = (columns || []).map(col => ({
                    label: {
                        label: col[0].padEnd(40, " "),
                        description: col[1],
                    },
                    sortText: col[2],
                    detail: "Tabela do banco",
                    documentation: "Tabela usada para armazenar dados de clientes.",
                    kind: monaco.languages.CompletionItemKind.Variable,
                    insertText: col[0]
                }));

                return { suggestions };
            }
        });


        editor = monaco.editor.create(
            document.getElementById("editor-container"),
            {
                value: "SELECT * FROM cmf",
                language: "sql",
                theme: "vs-dark",
                automaticLayout: true,
                fontSize: 12,
                minimap: { enabled: true }
            }
        );

        editor.addCommand(monaco.KeyCode.F8, () => js_db_execute());
        editor.addCommand(monaco.KeyCode.F5, () => js_db_explain());
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyE,() => js_recall_sql_form());



        editor.addAction({
            id: "Describe Table",
            label: "Describe Table",
            keybindings: [],
            contextMenuGroupId: "navigation",
            contextMenuOrder: 1.5,

            run: function (ed) {
                obj = get_sql_editor();
                if (window.object_tables.includes(obj.toUpperCase())) {
                    js_db_describe(obj);
                } else {
                    alert("Table Not Found!");
                }
            }
        });

        window.editorSQL = editor;
    });
}


function js_file_open() {
    const fileInput = document.getElementById('fileInput');
    fileInput.value = '';
    fileInput.click();

    fileInput.onchange = (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        const reader = new FileReader();
        window.file_name = file.name;
        id_menu_filename.innerHTML = window.file_name;
        reader.onload = (e) => {
            const content = e.target.result;
            window.editorSQL.setValue(content);
        };
        reader.readAsText(file);
    };
}