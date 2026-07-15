var global_var = {};

function base64ToString(base64) {
    const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
    return new TextDecoder("utf-8").decode(bytes);
}

function stringToBase64(texto) {
    const bytes = new TextEncoder().encode(texto);
    return btoa(String.fromCharCode(...bytes));
}


function detectMimeType(base64) {
    // Remove o prefixo caso seja um Data URI
    base64 = base64.replace(/^data:.*;base64,/, "");

    // Decodifica apenas o início
    const bytes = Uint8Array.from(atob(base64.substring(0, 64)), c => c.charCodeAt(0));

    // PDF
    if (bytes.length >= 4 &&
        bytes[0] === 0x25 &&
        bytes[1] === 0x50 &&
        bytes[2] === 0x44 &&
        bytes[3] === 0x46)
        return "application/pdf";

    // PNG
    if (bytes.length >= 8 &&
        bytes[0] === 0x89 &&
        bytes[1] === 0x50 &&
        bytes[2] === 0x4E &&
        bytes[3] === 0x47 &&
        bytes[4] === 0x0D &&
        bytes[5] === 0x0A &&
        bytes[6] === 0x1A &&
        bytes[7] === 0x0A)
        return "image/png";

    // JPEG
    if (bytes.length >= 3 &&
        bytes[0] === 0xFF &&
        bytes[1] === 0xD8 &&
        bytes[2] === 0xFF)
        return "image/jpeg";

    // GIF
    if (bytes.length >= 6) {
        const s = String.fromCharCode(...bytes.slice(0, 6));
        if (s === "GIF87a" || s === "GIF89a")
            return "image/gif";
    }

    // BMP
    if (bytes.length >= 2 &&
        bytes[0] === 0x42 &&
        bytes[1] === 0x4D)
        return "image/bmp";

    // TIFF
    if (bytes.length >= 4 &&
        (
            (bytes[0] === 0x49 && bytes[1] === 0x49 &&
                bytes[2] === 0x2A && bytes[3] === 0x00)
            ||
            (bytes[0] === 0x4D && bytes[1] === 0x4D &&
                bytes[2] === 0x00 && bytes[3] === 0x2A)
        ))
        return "image/tiff";

    // ZIP / DOCX / XLSX / PPTX / ODT / JAR...
    if (bytes.length >= 4 &&
        bytes[0] === 0x50 &&
        bytes[1] === 0x4B &&
        bytes[2] === 0x03 &&
        bytes[3] === 0x04)
        return "application/zip";

    // RAR
    if (bytes.length >= 6 &&
        bytes[0] === 0x52 &&
        bytes[1] === 0x61 &&
        bytes[2] === 0x72 &&
        bytes[3] === 0x21)
        return "application/vnd.rar";

    // 7Z
    if (bytes.length >= 6 &&
        bytes[0] === 0x37 &&
        bytes[1] === 0x7A &&
        bytes[2] === 0xBC &&
        bytes[3] === 0xAF)
        return "application/x-7z-compressed";

    // XML
    if (bytes.length >= 5) {
        const s = String.fromCharCode(...bytes.slice(0, 5));
        if (s === "<?xml")
            return "application/xml";
    }

    return "text/plain";
}


function playBip() {
    if (global_var.bip == '1') {
        const ctx = new AudioContext();

        [600, 900].forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.frequency.value = freq;
            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start(ctx.currentTime + i * 0.15);
            osc.stop(ctx.currentTime + i * 0.15 + 0.1);
        });
    }
}


function downloadString(conteudo, nomeArquivo = "arquivo.txt") {
    const blob = new Blob([conteudo], { type: "text/plain;charset=utf-8" });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = nomeArquivo;

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function clearTable(table) {
    const clone = table.cloneNode(true);

    clone.querySelectorAll("*").forEach(el => {
        el.removeAttribute("style");
        el.removeAttribute("class");
        el.removeAttribute("onclick");
    });

    clone.removeAttribute("style");
    clone.removeAttribute("class");
    clone.removeAttribute("onclick");

    return clone.outerHTML;
}


function configureTheme(theme) {
    id_theme_css.href = '/css/' + theme;
    let edt = theme == "style-dark.css" ? 'vs-dark' : 'vs';
    global_var.editorSQL.updateOptions({ theme: edt });
}

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
}

function toSingleTable(dat) {
    const table = document.createElement("table");
    for (const [key, value] of Object.entries(dat)) {
        const tr = document.createElement("tr");
        const tdKey = document.createElement("td");
        tdKey.textContent = key;
        const tdValue = document.createElement("td");
        const pre = document.createElement("pre");
        pre.textContent = value == null ? "" : String(value);
        tdValue.appendChild(pre);
        tr.appendChild(tdKey);
        tr.appendChild(tdValue);
        table.appendChild(tr);
    }
    return table.outerHTML;
}


function showMemoArea(content) {
    if (content == '@grid') {
        id_dbms_output.style.display = 'none';
        id_grid_dados.style.display = 'block';
        id_grid_dados_pager.style.display = 'block';
    } else {
        id_dbms_output.style.display = 'block';
        id_grid_dados.style.display = 'none';
        id_grid_dados_pager.style.display = 'none';
        id_dbms_output_data.innerHTML = content;
    }
}


function showTab(btn) {
    let bloco = btn.parentNode.parentNode;
    bloco.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    bloco.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
    bloco.querySelectorAll('div[tag="tab' + btn.getAttribute('tag') + '"]').forEach(t => t.classList.add('active'));
    btn.classList.add('active');
}


function toChar(date, mask = 'DD/MM/YYYY HH24:MI:SS') {
    const pad = n => String(n).padStart(2, '0');
    return mask
        .replace('DD', pad(date.getDate()))
        .replace('MM', pad(date.getMonth() + 1))
        .replace('YYYY', date.getFullYear())
        .replace('HH24', pad(date.getHours()))
        .replace('MI', pad(date.getMinutes()))
        .replace('SS', pad(date.getSeconds()));
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

    if (usingHeader == false) {
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
            // sessão expirou
            if (response.status === 401) {
                window.location.href = "/login";
                return;
            }

            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then(a => {
            if (a == null) {
                return;
            }

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


function change_icon(running = null) {
    let idx = id_login_database.selectedIndex;
    let text = idx >= 0 ? id_login_database.options[idx].innerText : "";
    let caption = idx >= 0 ? id_login_username.value + "@" + text : "";

    if (running == null) {
        document.title = "🔵 - AlgarSQL";
        id_menu_db.innerHTML = "";
        id_tree_obj.innerHTML = '';
        id_tree_obj.index = 0;
        return;
    }
    document.title = (running ? "🔴" : "🔵") + " " + caption;
    id_menu_db.innerHTML = caption;
}


function js_dbtree_show() {
    id_tree_obj.innerHTML = id_tree_obj.value ?? 'No Connection Found';
    id_tree_obj.index = 0;
}

function js_tree_login_saved(x) {
    d = x.getAttribute("nodeInfo").split("/");
    id_login_database.selectedIndex = Array.from(id_login_database.options).findIndex(opt => opt.text === d[2]);
    id_login_username.value = d[0].split("|")[1];
    id_login_password.value = d[1];
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

            if (c === ';') {
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
        }
    }

    return text.substring(start, end).trim();
}



function get_sql_editor_portion() {
    var editor = global_var.editorSQL;

    const model = editor.getModel();
    const position = editor.getPosition();
    const offset = model.getOffsetAt(position);

    return getStatementAtCursor(global_var.editorSQL.getValue(), offset - 1);
}


function get_sql_editor() {
    if (id_div_compiler.style.display == 'flex') {
        return global_var.editorSQL.getValue();
    }

    const selection = global_var.editorSQL.getSelection();
    const selectedText = global_var.editorSQL.getModel().getValueInRange(selection);
    let finalText = selectedText;

    if (!selectedText) {
        finalText = get_sql_editor_portion();
    }
    return finalText;
}




function jsExportToFile(sql, type) {
    table_name = "";
    if (type == 0) {
        table_name = prompt("Table Name", "table_name");
    }

    id_message_box_form.style.display = "flex";
    id_message_box_text.innerHTML = "Exporting...";

    var formData = {
        action: "export_to_file",
        type: type,
        table_name: table_name,
        sql: sql
    };

    ajax("/db_execute", formData, function (a) {
        js_global_thread_status(id_message_box_form, id_message_box_text);
    });
}


/*
    ==========================================================================================------------------------------------
    comment: Funcoes para embelezar e formatar o codigo PL/SQL, utilizando uma chamada ao servidor para processar o código e retornar uma versão formatada, que é então exibida no editor SQL.
    ==========================================================================================------------------------------------
*/


function js_format_plsql() {
    const selection = global_var.editorSQL.getSelection();
    const selectedText = global_var.editorSQL.getModel().getValueInRange(selection);

    if (!selectedText) {
        alert("Select the PL/SQL code to format.");
        return;
    }

    ajax("/format_plsql", { "code": selectedText }, function (a) {
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
    if (id_div_compiler_spec.innerText == 'body') {
        id_div_compiler_spec.spec = global_var.editorSQL.getValue();
        id_div_compiler_spec.specVS = global_var.editorSQL.saveViewState();
        id_div_compiler_spec.innerText = 'spec';
        global_var.editorSQL.setValue(id_div_compiler_spec.body);
        global_var.editorSQL.restoreViewState(id_div_compiler_spec.bodyVS);

    } else {
        id_div_compiler_spec.body = global_var.editorSQL.getValue();
        id_div_compiler_spec.bodyVS = global_var.editorSQL.saveViewState();
        id_div_compiler_spec.innerText = 'body';
        global_var.editorSQL.setValue(id_div_compiler_spec.spec)
        global_var.editorSQL.restoreViewState(id_div_compiler_spec.specVS);
    }
    global_var.editorSQL.focus();
}


function js_editor_mode_open(object_name) {
    change_icon(true);
    ajax("/db_execute", { "action": "ddl", "object_name": object_name }, function (a) {
        if (a.status_code != 0) {
            alert(a.status_msg);
            return;
        }

        var code = a.ddl.split("<end_package_spec>");
        global_var.editorSQL.setValue(code[0].trim());
        if (code.length > 1) {
            id_div_compiler_spec.style.display = 'flex';
            id_div_compiler_spec.innerText = 'body';
            id_div_compiler_spec.spec = code[0].trim();
            id_div_compiler_spec.body = code[1].trim();
            id_div_compiler_spec.specVS = null;
            id_div_compiler_spec.bodyVS = null;
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

    ajax("/th_status", { _: Date.now() }, function (a) {
        id_logger_text.innerHTML = a.status_msg;
        if (a.status_code != 0) {
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

function js_workdata_import_populate() {
    if (confirm('Populate workdata model with this query?')) {
        ajax("/db_execute", { "action": "workdata_import", "sql": id_workdata_import_query.value },
            function (a) {
                js_global_thread_status(id_workdata_form, id_workdata_import_status);
            }
        );
    }
}

function js_workdata_import_view() {
    ajax("/config_workdata_load", {}, function (a) {
        global_var.grid_workdata_import.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100,
            []
        );
        global_var.grid_workdata_import.desenharTabela();
    }, null, false);
}


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
        js_global_thread_status(id_workdata_form, id_csv_completer_status);
    }, null, false);
}

function js_workdata_form() {
    id_workdata_form.style.display = "flex";
}



/*
    ==========================================================================================------------------------------------
    comment: Função para abrir um template SQL salvo, permitindo ao usuário selecionar um arquivo de template e carregar seu conteúdo no editor SQL.
    ==========================================================================================-------------------------------------
*/

function js_template_save_opened() {
    if (id_menu_template_name.innerText != "") {
        ajax("/template", {
            "action": "save",
            "name": id_menu_template_name.innerText,
            "value": global_var.editorSQL.getValue()
        },
            function (a) { }
        );
    }
}


function js_template_close() {
    if ( confirm("Are you sure you want to close this template?") ) {
        id_menu_template_name.innerText = "";
        global_var.editorSQL.setValue("select * from dual");
    }
}

function js_templates_open_item(x) {
    if (confirm('Open this template in new editor?')) {
        ajax("/template", { "action": "open", "name": x.getAttribute("nodeInfo") }, function (a) {
            global_var.tmp_template_name = x.getAttribute("nodeInfo");
            global_var.tmp_template_code = a.code;
            window.open("/?template");
        });
    }
}

function js_template_load(node_filter = null) {
    if (id_tree_obj.index == 0) {
        id_tree_obj.value = id_tree_obj.innerHTML;
    }

    ajax("/template", { "action": "load" }, function (a) {
        id_tree_obj.innerHTML = global_var.tree_templates.montaArvoreDados(a.templates);
        id_tree_obj.index = 1;

        global_var.tree_templates.goToNode(node_filter);

        global_var.tree_templates.preparePopupMenu(id_tree_obj, id_popup_template, function (acao, tobj) {
            var info = tobj.getAttribute("nodeInfo");
            var type = tobj.getAttribute("nodeType");
            var newName = "-";
            var dat = info.split("|");
            var no_to_find = info;

            if (type == "FILE") {
                no_to_find = tobj.parentElement.parentElement.parentElement.querySelector("a[nodeType='FOLDER']").getAttribute("nodeInfo");
            }

            if (acao == "rename") {
                newName = prompt("New Name", dat.at(-1));
                if (!newName) {
                    return;
                }
                dat[dat.length - 1] = newName;
            }
            if (acao == "newfile") {
                newName = prompt("New File", "newfile.sql");
                if (!newName) {
                    return;
                }
                dat.push(newName);
            }
            newName = dat.join("|");

            if (acao == "moveto") {
                newName = prompt("Move to:", info);
                if (!newName) {
                    return;
                }
                no_to_find = newName;
                acao = "rename";
            }

            ajax("/template", { "action": acao, "name": info, "type": type, "new_name": newName, "value": global_var.editorSQL.getValue() }, function (a) {
                alert(a.status_msg);
                js_template_load(no_to_find);
            });
        });
    });
}

/*
    ==========================================================================================------------------------------------
    comment: Funções relacionadas à funcionalidade de "Find Object", que permite a
    o usuário buscar objetos no banco de dados por nome.
    ==========================================================================================------------------------------------
*/


function js_find_object_execute() {
    id_find_object_grid.innerHTML = '';
    ajax("/db_execute", { "action": "findobj", "object_name": id_find_object_name.value, "code_text": id_find_code_text.value }, function (a) {
        if (a.status_code != 0) {
            alert(a.status_msg);
            return;
        }
        global_var.grid_find_objects.setContent(
            a.data,
            a.columns,
            a.columns_types,
            100,
            [
                { texto: 'DDL', funcao: function (item) { js_ddl_view(item.OWNER + '...' + item.OBJECT_TYPE + '...' + item.OBJECT_NAME); } },
                { texto: 'edit', funcao: function (item) { js_editor_mode_open(item.OWNER + '...' + item.OBJECT_TYPE + '...' + item.OBJECT_NAME); } },
                { texto: 'export', funcao: function (item) { js_ddl_view(item.OWNER + '...' + item.OBJECT_TYPE + '...' + item.OBJECT_NAME, true); } }
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
                {
                    texto: 'copy',
                    funcao: function (item) {
                        copyToClip(item.SQL);
                        alert('Copied to Clipboard!');
                    }
                }
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
    comment: Funções relacionadas à configuração de preferências do usuário, 
    como diretórios de templates e arquivos de configuração,
    ==========================================================================================------------------------------------
*/

function js_preferences_tnsnames() {
    ajax("/config_get_tnsnames", {}, function (a) {
        js_window_popup("TNSNAMES.ORA", a.tnsnames);
    });
}

function js_preferences_form(x = "flex") {
    ajax("/config_get", {}, function (a) {
        id_preferences_tns.value = a.tns;
        id_preferences_tns_saved.value = a.tnsSaved;
        id_preferences_monaco_theme.value = a.monacoTheme;
        id_preferences_bip.value = a.bip;
        id_preferences_form.style.display = x;
        configureTheme(a.monacoTheme);
    });
}

// Salva as preferências do usuário, enviando os dados para o servidor e atualizando a interface conforme necessário.
function js_preferences_save() {
    r = {
        "tns": id_preferences_tns.value,
        "tnsSaved": id_preferences_tns_saved.value,
        "monacoTheme": id_preferences_monaco_theme.value,
        "bip": id_preferences_bip.value
    };

    ajax("/config_save", r, function (a) {
        alert(a.status_msg);
        id_preferences_form.style.display = "none";
        configureTheme(id_preferences_monaco_theme.value);
        global_var.config_loaded = false;
        global_var.bip = id_preferences_bip.value;
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
            if (confirm("Change password for user " + a.db_user + "@" + id_login_database.options[id_login_database.selectedIndex].innerText + "?")) {
                ajax("/db_execute", { "action": "change_password", "db_tns": a.db_tns, "db_user": a.db_user, "db_password": id_login_password.value }, async function (a) {
                    alert(a.status_msg);
                });
            }
        }
    });
}

function js_login_connect() {
    ajax("/db_execute", {
        "action": "connect",
        "usr": id_login_username.value,
        "pwd": id_login_password.value,
        "tns": id_login_database.value,
        "direct": id_login_direct.value
    }, async function (a) {
        if (a.status_code == 0) {
            ret1 = global_var.tree_objects.montaArvoreDados(a.tree);
            id_tree_obj.innerHTML = ret1;
            id_tree_obj.index = 0;
            id_login_form.style.display = "none";
            global_var.object_tables = a.object_tables;
            global_var.object_users = a.object_users;
            change_icon(false);
        } else {
            alert(a.status_msg);
            change_icon();
        }
    });
}


function js_login_form() {
    ajax("/config_get", {}, function (a) {
        id_login_form.style.display = "flex";

        if (global_var.config_loaded == false) {
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
                if (x[i].includes("##") == false && x[i].indexOf("|") >= 0) {
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
    comment: Editor da Grid
    ==========================================================================================------------------------------------
*/


function js_db_grid_editrow(row, columns, columns_types) {
    const container = document.getElementById('id_edit_row_grid_content');
    container.innerHTML = '';
    container.row = row;
    id_edit_row_bt_save.style.display = 'none';

    columns.forEach((c, idx) => {
        if (idx === 0) return;

        valor = row.cells[idx].value;

        if (c.toUpperCase() == "ROWID") {
            container.rowid = valor;
            id_edit_row_bt_save.style.display = '';
        } else {
            if ( columns_types[idx - 1].includes("BLOB") ) {
                valor = base64ToString(valor);
            }
            const tr = document.createElement('tr');
            const td1 = document.createElement('td');
            td1.textContent = c;

            const td2 = document.createElement('td');
            const is_textarea = columns_types[idx - 1].includes("LOB") || String(valor).includes("\n");
            const input = document.createElement(is_textarea ? 'textarea' : 'input');
            input.type = 'text';
            input.id = `id_row_edit_field_${c}`;
            input.value = valor;
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
        valor = document.getElementById('id_row_edit_field_' + v).value;
        if ( global_var.grid_query.columns_types[idx - 1].includes("BLOB") ) {
            valor = stringToBase64(valor);
        }
        itens[v]       = valor;
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
        if (a.status_code == 0) {
            js_db_status(in_transaction = true);

            global_var.grid_query.columns.forEach((v, idx) => {
                if (idx == 0 || v == 'ROWID') return;
                td = id_edit_row_grid_content.row.cells[idx];
                if (global_var.grid_query.columns_types[idx - 1].includes("LOB") == false) {
                    td.innerText = document.getElementById('id_row_edit_field_' + v).value;
                }
                td.value = document.getElementById('id_row_edit_field_' + v).value;
            });
        }
    });

}

/*
    ==========================================================================================------------------------------------
    comment: Funções para extracao de DDL
    ==========================================================================================------------------------------------
*/


function js_ddl_view(obj, exp = false) {
    object_name = obj;
    if (obj instanceof Element) {
        object_name = obj.getAttribute("nodeInfo").replaceAll("|", "...");
    }
    change_icon(true);
    if (exp) {
        id_message_box_form.style.display = 'flex';
        id_message_box_text.innerHTML = "Saving DDL...";
    }
    ajax("/db_execute", { "action": "ddl", "object_name": object_name }, function (a) {
        if (a.status_code != 0) {
            alert(a.status_msg);
            return;
        }
        if (exp) {
            downloadString(a.ddl, object_name + ".sql");
            id_message_box_text.innerHTML = "Downloaded Sucess...";
        } else {
            js_window_popup("DDL: " + object_name, a.ddl);
        }
        change_icon(false);
    });
}


/*
    ==========================================================================================------------------------------------
    comment: Funções de banco de dados
    ==========================================================================================------------------------------------
*/

function js_db_execute_proc(obj) {
    ajax("/db_execute", { "action": "test_procedure", "object_name": obj }, function (a) {
        js_window_popup("TEST PROCEDURE", a.status_msg);
    });
}

function js_db_status(in_transaction = null, in_running = null, is_connected = null) {
    if (in_transaction != null) {
        id_menu_commit.disabled = !in_transaction;
        id_menu_rollback.disabled = !in_transaction;
    }
}

function js_db_execute() {
    js_template_save_opened();

    id_grid_dados.innerHTML = '';
    sql = get_sql_editor();

    if (sql.length < 3) {
        alert('No SQL Avalilable!');
        return;
    }

    change_icon(true);
    global_var.tm_elapsed.start();
    showMemoArea("Running...");

    ajax("/db_execute", { "action": "execute", "sql": sql }, function (a) {
        global_var.tm_elapsed.stop();

        global_var.last_output = toSingleTable({
            "status": `${a.status_code} - ${a.status_msg}`,
            "output": a.dbms,
            "sql": sql
        });

        if (a.status_code != 0) {
            showMemoArea(global_var.last_output);
            change_icon(false);
            return;
        }

        if (a.sql_type == 1) {
            showMemoArea('@grid');
            global_var.grid_query.setContent(a.data, a.columns, a.columns_types, 50, [], sql);
            global_var.grid_query.desenharTabela();
        } else {
            showMemoArea(global_var.last_output);
            js_db_status(in_transaction = true);
            playBip();
        }
        change_icon(false);
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
        let last_output = toSingleTable({
            "status_code": a.status_code,
            "status_msg": a.status_msg,
            "timestamp": Date()
        });

        if (a.status_code != 0) {
            alert(last_output);
            return;
        }
        showMemoArea(a.explain);
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
                js_window_popup("DESCRIBE: " + obj, a.describe, 'text/html');
            }
        );
    } else {
        alert("Table Not Found!");
    }

}

function js_db_fetch50(grid) {
    change_icon(true);
    ajax("/db_execute", { "action": "fetch", }, function (a) {
        if (a.data.length > 0) {
            grid.dados = grid.dados.concat(a.data);
            grid.paginaAtual++;
            grid.desenharTabela();
        } else {
            grid.btnNext.disabled = true;
        }
        change_icon(false);
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


function createEditorSQL(sql_autostart) {
    return new Promise((resolve) => {
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

                    if (in_list_table || in_list_users) {
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
                    value: sql_autostart ?? "SELECT * FROM cmf",
                    language: "sql",
                    theme: id_theme_css.href.includes("dark") ? "vs-dark" : "vs",
                    automaticLayout: true,
                    fontSize: 12,
                    minimap: { enabled: true }
                }
            );

            editor.addAction({
                id: "Recall Query",
                label: "Recall Query",
                keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyE],
                contextMenuGroupId: "navigation",
                contextMenuOrder: 1.5,
                run: () => js_recall_sql_form()
            });

            editor.addAction({
                id: "Execute Query",
                label: "Execute Query",
                keybindings: [monaco.KeyCode.F8, monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
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
                run: () => js_db_execute_proc(get_sql_editor())
            });


            editor.addAction({
                id: "Explain Query",
                label: "Explain Query",
                keybindings: [monaco.KeyCode.F5],
                contextMenuGroupId: "navigation",
                contextMenuOrder: 1.5,
                run: () => js_db_explain()
            });

            editor.addAction({
                id: "Open Local File",
                label: "Open Local File",
                keybindings: [],
                contextMenuGroupId: "1-files",
                contextMenuOrder: 1.5,
                run: () => js_window_fileopen()
            });

            editor.addAction({
                id: "Close Template",
                label: "Close Template",
                keybindings: [],
                contextMenuGroupId: "1-files",
                contextMenuOrder: 1.5,
                run: () => js_template_close()
            });

            editor.addAction({
                id: "Format PlSql",
                label: "Format PlSql",
                keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF],
                contextMenuGroupId: "coders",
                contextMenuOrder: 1.5,
                run: () => js_format_plsql()
            });
            resolve(editor);
        });
    });
}



function prepareSpliter() {
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



async function configuraAutoStart(configBip) {
    var sql_autostart = null;

    if (window.location.href.indexOf("?template") >= 0) {
        sql_autostart = window.opener.global_var.tmp_template_code;
        id_menu_template_name.innerText = window.opener.global_var.tmp_template_name;
        id_tree_obj.innerHTML = window.opener.id_tree_obj.innerHTML;
        id_tree_obj.index = 1;
    }

    if (window.location.href.indexOf("?openfile") >= 0) {
        sql_autostart = window.opener.global_var.tmp_datafile;
    }

    global_var = {
        object_tables: [],
        object_users: [],
        session_id: Date.now().toString(),
        tm_elapsed: new TTimer(function () {
            id_menu_stop.disabled = false;
            id_menu_execute.disabled = true;
        },
            function () {
                id_menu_stop.disabled = true;
                id_menu_execute.disabled = false;
            },
            function (e) {
                id_menu_timer.innerHTML = e;
            }
        ),
        grid_query: new TGrid("id_grid_dados", { "fetch": true, "export": true, "edit": true }),
        grid_find_objects: new TGrid("id_find_object_grid"),
        grid_view_sessions: new TGrid("id_view_sessions_grid"),
        grid_recall_sql: new TGrid("id_recall_sql_grid"),
        grid_workdata_import: new TGrid("id_workdata_import_grid"),
        tree_login: new TreeView('log'),
        tree_objects: new TreeView('obj'),
        tree_templates: new TreeView('tem'),
        config_loaded: false,
        editorSQL: await createEditorSQL(sql_autostart),
        bip: configBip,
        last_output: ""
    };

    global_var.grid_query.fetch_on_next_button = true;
    global_var.tree_objects.endNodeClick = "js_ddl_view";
    global_var.tree_login.endNodeClick = "js_tree_login_saved";
    global_var.tree_login.endNodeText = "nodeValue.split('/')[0] + '@' + nodeValue.split('/')[2]";
    global_var.tree_templates.endNodeClick = "js_templates_open_item";
    global_var.tree_templates.endNodeText = "nodeValue.split('|').at(-1)";


    prepareSpliter();


    window.addEventListener("beforeunload", function (e) {
        localStorage.setItem('F5-CONTENT', global_var.editorSQL.getValue());
        localStorage.setItem('F5-TEMPLATE', id_menu_template_name.innerText);
        e.preventDefault();
        e.returnValue = "";
    });

    document.body.style.display = "block";

    if (window.location.href.indexOf("?tab") >= 0) {
        id_login_database.innerHTML = window.opener.id_login_database.innerHTML;
        id_login_direct.innerHTML = window.opener.id_login_direct.innerHTML;
        id_login_username.value = window.opener.id_login_username.value;
        id_login_password.value = window.opener.id_login_password.value;
        id_login_database.value = window.opener.id_login_database.value;
        id_login_direct.value = window.opener.id_login_direct.value;
        js_login_connect();
    }


    history.pushState(null, '', '/');

    var f5_data = localStorage.getItem('F5-CONTENT');
    var f5_template = localStorage.getItem('F5-TEMPLATE');

    if (sql_autostart == null && f5_data != null) {
        global_var.editorSQL.setValue(f5_data);
        localStorage.removeItem('F5-CONTENT');
    }

    if (sql_autostart == null && f5_template != null) {
        id_menu_template_name.innerText = f5_template;
        localStorage.removeItem('F5-TEMPLATE');
    }

}



function js_window_popup(name, content, tp = 'text/plain') {
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
           <pre><xxxx></pre>
        </body>
    `;
    blob = new Blob([content], { type: tp });

    if ( name.includes("BLOB") ) {
        tp    = detectMimeType(content);
        bytes = Uint8Array.from(atob(content), c => c.charCodeAt(0)); 
        blob = new Blob([bytes], { type: tp });
    }
    if ( tp.includes("html") ) {
        blob = new Blob([page.replaceAll('<xxxx>', content)], { type: tp });;
    }
    x = window.open(URL.createObjectURL(blob), name);
    return x;
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
            global_var.tmp_datafile = content;
            window.open("/?openfile")
        };
        reader.readAsText(file);
    };
}
