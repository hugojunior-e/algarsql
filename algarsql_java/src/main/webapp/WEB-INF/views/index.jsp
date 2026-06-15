<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>

    <!DOCTYPE html>
    <html lang="pt-br">

    <head>
        <meta charset="UTF-8">
        <title>AlgarSQL</title>

        <script src="https://unpkg.com/monaco-editor@0.52.2/min/vs/loader.js"></script>

        <link id="id_theme_css" rel="stylesheet" href="/css/${monacoTheme}">
        <script src="/js/funcs.js"></script>
        <script src="/js/tree.js"></script>
        <script src="/js/grid.js"></script>
        <script src="/js/localdb.js"></script>
        <script src="/js/timer.js"></script>
    </head>

    <body style="display: none;">
        <div class="menu">
            <button onclick="js_login_form()" class="tooltip">
                <span class="tooltiptext">Logon DB!</span>
                <img src="/imgs/db_logon.png">
            </button>

            <button onclick="js_logoff_form()" class="tooltip">
                <span class="tooltiptext">Logoff DB!</span>
                <img src="/imgs/db_logoff.png">
            </button>

            <button onclick="window.open('/?tab')" class="tooltip">
                <span class="tooltiptext">Open New Window DB!</span>
                <img src="/imgs/file_new.png">
            </button>

            <span class="separator"></span>

            <button id="id_menu_execute" onclick="js_db_execute()" class="tooltip">
                <span class="tooltiptext">F8 - Execute SQL</span>
                <img src="/imgs/sql_run.png">
            </button>

            <button id="id_menu_stop" onclick="js_db_stop()" class="tooltip" disabled>
                <span class="tooltiptext">Stop SQL</span>
                <img src="/imgs/sql_stop.png">
            </button>

            <span class="separator"></span>

            <button id="id_menu_commit" onclick="js_db_transaction('commit')" disabled class="tooltip">
                <span class="tooltiptext">Commit</span>
                <img src="/imgs/sql_commit.png">
            </button>

            <button id="id_menu_rollback" onclick="js_db_transaction('rollback')" disabled class="tooltip">
                <span class="tooltiptext">Rollback</span>
                <img src="/imgs/sql_rollback.png">
            </button>

            <span class="separator"></span>

            <button onclick="js_csv_completer_form()" class="tooltip">
                <span class="tooltiptext">Csv Completer</span>
                <img src="/imgs/csv.png">
            </button>

            <button onclick="js_preferences_form()" class="tooltip">
                <span class="tooltiptext">Preferences</span>
                <img src="/imgs/preferences.png">
            </button>

            <span class="separator"></span>

            <span style="cursor:pointer" onclick="js_view_sessions_form()" class="tooltip">
                <span class="tooltiptext">View Sessions</span>
                <span id="id_menu_db"></span>
            </span>

            <span class="separator"></span>
            <span id="id_menu_timer" style="width:100px;text-align: center;">00:00:00</span>

            <span class="separator"></span>
            [<span id="id_menu_template_name" style="color:Red;font-weight: bold"></span>]


            <div id="id_title_page" style="margin-left:auto; font-size:14px;">
                <a href="/login">[ Logout: ${login} ]</a>
            </div>

        </div>

        <div class="main">
            <div class="sidebar">
                <div
                    style="overflow:hidden;display:flex;justify-content:center;gap:10px;font-weight: bold;border: 1px solid #1e0101;">
                    <a href=# onclick="js_dbtree_show()">DB</a>
                    <span>|</span>
                    <a href=# onclick="js_template_load()">TEMPLATES</a>
                    <span>|</span>
                    <a href=# onclick="js_find_object_form()">FIND</a>
                </div>
                <div style="height:10px;"></div>
                <div id="id_tree_obj"></div>
            </div>

            <!-- SPLITTER VERTICAL -->
            <div class="splitter-vertical" id="vsplit"></div>

            <!-- PAINEL DIREITO -->
            <div class="right">
                    <!-- CONTAINER DO MONACO -->
                    <div id="editor-container"></div>

                    <!-- SPLITTER HORIZONTAL -->
                    <div class="splitter-horizontal" id="hsplit"></div>

                    <!-- GRID RESULTADO -->
                    <div class="grid">
                        <table id="id_grid_dados"></table>
                        <div id="id_dbms_output" style="display: none;">
                            <pre id="id_dbms_output_data" style="padding: 0 10px;"></pre>
                        </div>
                    </div>
                    <div id="id_grid_dados_pager"></div>
            </div>
        </div>


        <input type="file" id="fileInput" hidden>

        <!--
        FORM MESSAGE BOX
        -->

        <div id="id_message_box_form" class="itools_modal">
            <div class="dialog" style="width:400px;height:20%">
                <div class="header">
                    <span>MessageBox</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>
                <div class="content">
                    &nbsp;&nbsp;<div id="id_message_box_text"></div>
                </div>
            </div>
        </div>


        <!--
        FORM RECALL SQL
        -->
        <div id="id_recall_sql_form" class="itools_modal">
            <div class="dialog" style="width:80%;height:80%">
                <div class="header">
                    <span>Recall SQL</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>

                <div class="content flex">
                    <table>
                        <tr>
                            <td>Database:</td>
                            <td><input type="text" id="id_recall_sql_database" value="%"></td>
                            <td>text:</td>
                            <td><input type="text" id="id_recall_sql_text" value="%"></td>
                            <td><button onclick="js_recall_sql_execute()">Find</button></td>
                        </tr>
                    </table>
                    <div class="grid">
                        <table id="id_recall_sql_grid">
                        </table>
                    </div>
                    <div id="id_recall_sql_grid_pager" class="pager"></div>
                </div>
            </div>
        </div>

        <!--
        FORM FIND OBJECT
        -->
        <div id="id_find_object_form" class="itools_modal">
            <div class="dialog" style="width:80%;height:80%">
                <div class="header">
                    <span>Find Object</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>

                <div class="content flex">
                    <table>
                        <tr>
                            <td>Type Object Name:</td>
                            <td><input type="text" id="id_find_object_name" value="%"></td>
                            <td><button onclick="js_find_object_execute()">Find Obj</button></td>
                        </tr>
                    </table>
                    <div class="grid">
                        <table id="id_find_object_grid">
                        </table>
                    </div>
                    <div id="id_find_object_grid_pager" class="pager"></div>
                </div>

            </div>
        </div>



        <!--
        FORM CSV COMPLETER
        -->
        <div id="id_csv_completer_form" class="itools_modal">
            <div class="dialog" style="width:1000px">
                <div class="header">
                    <span>CSV Completer</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>
                <div class="content">
                    <table>
                        <tr>
                            <td>Options?</td>
                            <td><select id="id_csv_completer_options">
                                    <option value="true" selected>Use first line as titles</option>
                                    <option value="false">Don't use first line as titles</option>
                                </select></td>
                        </tr>
                        <tr>
                            <td>File Name:</td>
                            <td><input type="file" id="id_csv_completer_filename"></td>
                        </tr>
                        <tr>
                            <td>Query data Completer:</td>
                            <td><textarea id="id_csv_completer_query" spellcheck="false"
                                    style="height:200px"></textarea>
                            </td>
                        </tr>
                        <tr>
                            <td></td>
                            <td><button onclick="js_csv_completer_execute()">Execute</button>
                                <pre id="id_csv_completer_status">-</pre>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>

        <!--
        FORM VIEW SESSIONS
        -->
        <div id="id_view_sessions_form" class="itools_modal">
            <div class="dialog" style="width:80%;height:80%">
                <div class="header">
                    <span>View Sessions</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>

                <div class="content flex">
                    <table>
                        <tr>
                            <td>Status:</td>
                            <td> <select id="id_view_sessions_status">
                                    <option value="ACTIVE">ACTIVE</option>
                                    <option value="INACTIVE">INACTIVE</option>
                                    <option value="%" selected>ALL</option>
                                </select></td>
                            <td><button onclick="js_view_sessions_execute()">View Sessions</button></td>
                        </tr>
                    </table>
                    <div class="grid">
                        <table id="id_view_sessions_grid">
                        </table>
                    </div>
                    <div id="id_view_sessions_grid_pager" class="pager"></div>
                </div>

            </div>
        </div>


        <!--
        FORM PREFERENCES
        -->

        <div id="id_preferences_form" class="itools_modal">
            <div class="dialog" style="width:80%;height:80%">
                <div class="header">
                    <span>Preferences</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>

                <div class="content">
                    <div class="tabs">
                        <div class="tab-btn active" tag="1" onclick="showTab(this)">
                            Tns Names
                        </div>

                        <div class="tab-btn" tag="2" onclick="showTab(this)">
                            Saved Users
                        </div>

                        <div class="tab-btn" tag="3" onclick="showTab(this)">
                            Others
                        </div>
                    </div>

                    <div tag="tab1" class="tab-content active">
                        <textarea id="id_preferences_tns" spellcheck="false"></textarea>
                    </div>

                    <div tag="tab2" class="tab-content">
                        <textarea id="id_preferences_tns_saved" spellcheck="false"></textarea>
                    </div>
                    <div tag="tab3" class="tab-content">
                        <table>
                            <tr>
                                <td>Monaco Theme:</td>
                                <td><select id="id_preferences_monaco_theme">
                                        <option value="style-dark.css">Dark</option>
                                        <option value="style-plsql.css">Light</option>
                                    </select></td>
                            </tr>

                            <tr>
                                <td>Bip on DML Executions:</td>
                                <td><select id="id_preferences_bip">
                                        <option value="1">Yes</option>
                                        <option value="0">No</option>
                                    </select></td>
                            </tr>                            
                        </table>
                    </div>

                    <button onclick="js_preferences_save()">Save</button>
                    <a href="#" onclick="js_preferences_load_tns()">Load tnsnames.ora</a>
                </div>
            </div>
        </div>



        <!--
        FORM EDIT ROW FOR GRID
        -->

        <div id="id_edit_row_grid_form" class="itools_modal">
            <div class="dialog" style="width:80%;height:80%">
                <div class="header">
                    <span>Edit Row</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>

                <div class="content">
                    <table id="id_edit_row_grid_content">
                    </table>
                    <button onclick="js_db_grid_editrow_save()" id="id_edit_row_bt_save">Save</button>
                </div>
            </div>
        </div>


        <!--
        FORM LOGIN
        -->


        <div id="id_login_form" class="itools_modal">
            <div class="dialog">
                <div class="header">
                    <span>Login Database</span>
                    <button class="close-btn"
                        onclick="this.parentElement.parentElement.parentElement.style.display='none'">&times;</button>
                </div>
                <div class="content" style="display: flex">
                    <div class="sidebar" id=id_login_list_tns_saved style="height: 300px; width:500px">
                    </div>
                    <table>
                        <tr>
                            <td>Username:</td>
                            <td><input type="text" id="id_login_username" value=""></td>
                        </tr>
                        <tr>
                            <td>Password:</td>
                            <td><input type="password" id="id_login_password" value=""></td>
                        </tr>
                        <tr>
                            <td>Database:</td>
                            <td><select id="id_login_database"></select></td>
                        </tr>
                        <tr>
                            <td>Con.Type:</td>
                            <td><select id="id_login_direct">
                                    <option value="1">direct</option>
                                    <option value="0" selected>userExec</option>
                                </select></td>
                        </tr>
                        <tr>
                            <td></td>
                            <td><button onclick="js_login_connect()">OK</button></td>
                        </tr>
                        <tr>
                            <td></td>
                            <td><a href=# onclick="js_login_change_password()">Change user Password</a></td>
                        </tr>
                        <tr>
                            <td></td>
                            <td><a href=# onclick="js_clear_cache()">Clear Cache Tree</a></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>



        <div id="id_div_compiler" class="div_modal_editor">
            <button onclick="js_editor_mode_close()"> [Close]</button>
            <button onclick="js_editor_mode_goto()" id="id_div_compiler_spec" style="display: none;">goto body</button>
        </div>


        <div class="popup-menu" id="id_popup_template">
            <div class="popup-item" tag=newfile tagCondition="FOLDER">New File</div>
            <div class="popup-item" tag=delete>Delete</div>
            <div class="popup-item" tag=rename>Rename</div>
            <div class="popup-item" tag=moveto>Move to</div>
        </div>     
        
        <div id="id_tooltip"></div>


        <script>
            configuraAutoStart('${bip}');
        </script>


    </body>

    </html>