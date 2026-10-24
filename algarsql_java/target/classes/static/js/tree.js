class TreeView {
    constructor(idd) {
        this.idd = idd;
        this.nodes = [];
        this.openNodes = [];
        this.treeBuffer = [];
        this.endNodeClick = null;
        this.endNodeText = null;
        this.treeIcones = ["🔵", "📁"];
        this.mais = "➕";
        this.isPopupMenuPrepared = false;
        this.clickedLink = null;
        this.children = new Map();
    }


    writeTreeString(txt) {
        this.treeBuffer.push(txt);
    }

    goToNode(no) {
        var lista = [];

        if ( no == null ) { return };
        var x = document.querySelector('a[nodeInfo="' + no + '"]');
        if ( x == null ) { return };

        if ( x.getAttribute("nodeType") == "FILE" ) {
            x = x.parentElement.parentElement.parentElement.querySelector("a[nodeType='FOLDER']");
        }

        var iid = x.id ?? "-";
        lista.push(x);
        while ( true ) {
            x   = x.parentElement;
            iid = x.id || "-";
            if ( iid == "id_tree_obj" ) {
                break;
            }
            var l = x.querySelector('a[nodeType="FOLDER"]');
            if ( l != null ) { 
                lista.push(l);
            }
        }
        Array.from(new Set(lista)).forEach(item => {
            if ( item.getAttribute("nodeType") == "FOLDER" ) {
                item.click();
            }
        });
    }

    montaArvoreDados(arrNodes, startNode = 0, openNode = null) {
        this.treeBuffer = [];
        this.nodes = this.parseCsvToTreeArray(arrNodes);

        this.children = new Map();

        for (const node of this.nodes) {
            if (!this.children.has(node.parent)) {
                this.children.set(node.parent, []);
            }
            this.children.get(node.parent).push(node);
        }        

        this.openNodes = [];

        if (this.nodes.length > 0) {
            const recursedNodes = [];
            this.addNode(startNode, recursedNodes);
        }

        return this.treeBuffer.join("\n");
    }

    preparePopupMenu(id_tree, id_popup, jsAction) {
        if (this.isPopupMenuPrepared == false) {
            id_popup.addEventListener("click", (e) => {
                const item = e.target.closest(".popup-item");
                if (!item) return;
                const acao = item.getAttribute("tag");
                jsAction(acao, this.clickedLink);
            });     

            window.addEventListener("click", (e) => {
                id_popup.style.display = "none";
            });   
            this.isPopupMenuPrepared = true;
        }

        id_tree.querySelectorAll("a").forEach(item => {
            item.addEventListener("contextmenu",(e)=>{
                e.preventDefault();
                this.clickedLink = item; 

                id_popup.querySelectorAll("[tagCondition]").forEach(item => {
                    const condition = item.getAttribute("tagCondition");
                    item.style.display = (condition == this.clickedLink.getAttribute("nodeType")) ? "block" : "none";
                });
                
                id_popup.style.display = "block";
                id_popup.style.left = e.pageX + "px";
                id_popup.style.top  = e.pageY + "px";
            });
        });
    }


    getArrayId(node) {
        for (let i = 0; i < this.nodes.length; i++) {
            const values = this.nodes[i].split("|");
            if (values[0] == node) return i;
        }
        return null;
    }

    setOpenNodes(openNode) {
        for (let i = 0; i < this.nodes.length; i++) {
            const nodeValues = this.nodes[i].split("|");
            if (nodeValues[0] == openNode) {
                this.openNodes.push(nodeValues[0]);
                this.setOpenNodes(nodeValues[1]);
            }
        }
    }

    isNodeOpen(node) {
        return this.openNodes.includes(node);
    }

    lastSibling(node, parentNode) {
        const children = this.children.get(parentNode);
        return children[children.length - 1].id === node;        
    }

    addNode(parentNode, recursedNodes) {
        const children = this.children.get(parentNode);
        if (!children) return;

        for (const x of children) {

            const nodeValues = [ x.id, x.parent, x.name, x.link ];

            if (nodeValues[1] == parentNode) {
                this.writeTreeString("<span>");

                const ls = this.lastSibling(nodeValues[0], nodeValues[1]);
                const hcn = this.children.has(nodeValues[0]);
                const ino = this.isNodeOpen(nodeValues[0]);

                // linhas do layout
                for (let g = 0; g < recursedNodes.length; g++) {
                    if (recursedNodes[g] == 1) this.writeTreeString("  ┊");
                    else this.writeTreeString("&nbsp;&nbsp;&nbsp;");
                }

                recursedNodes.push(ls ? 0 : 1);

                const vv_div = `${this.idd}_${nodeValues[0]}`;
                
                // Nó com filhos
                if (hcn) {
                    const isLast = ls ? 1 : 0;
                    
                    const linkHTML = `
                        <a href="#"
                            onclick="oc('${vv_div}_${nodeValues[0]}', ${isLast}); return false;"
                            nodeFolderID="div${vv_div}_${nodeValues[0]}"
                            nodeType="FOLDER"
                            nodeInfo="${nodeValues[3].replaceAll('...', '|')}">
                            ${this.mais}${this.treeIcones[1]}${nodeValues[2]}
                        </a>`;

                    this.writeTreeString(linkHTML);                    

                } else {
                    // Nó folha
                    this.writeTreeString( this.treeIcones[0] );
                    const nodeValue       = nodeValues[2];
                    let endNodeText       = nodeValue;

                    if ( this.endNodeText != null ) {
                        endNodeText = eval(this.endNodeText);
                    }

                    if ( this.endNodeClick != null ) {
                        const linkHTML = `
                            <a href="#"
                                nodeType="FILE"
                                nodeInfo="${nodeValues[3].replaceAll('...', '|')}"
                                onclick="${this.endNodeClick}(this)">
                                ${endNodeText}
                            </a>`;                        
                        this.writeTreeString(linkHTML);
                        
                    } else {
                        this.writeTreeString(endNodeText);
                    } 
                }
                this.writeTreeString("<br/>");

                // Se tiver filhos → abre div e recursa
                if (hcn) {
                    this.writeTreeString(`<div id="div${vv_div}_${nodeValues[0]}"`);
                    if (!ino) this.writeTreeString(` style="display: none;"`);
                    this.writeTreeString(">");

                    this.addNode(nodeValues[0], recursedNodes);

                    this.writeTreeString("</div>");
                }

                recursedNodes.pop();
                this.writeTreeString("</span>");
            }
            
        }
    }

    // parser CSV → array de strings "id|parent|name|link"
    parseCsvToTreeArray(csv) {
        const lines = csv.split("\n");
        const map = {};
        const result = [];
        let currentId = 1;

        for (let line of lines) {
            const parts = line.trim().split("|");
            let path = "";
            let parentPath = "";
            let parentId = 0;

            for (let i = 0; i < parts.length; i++) {
                parentPath = path;
                path = path ? path + "|" + parts[i] : parts[i];

                if (!(path in map)) {
                    const id = currentId++;
                    map[path] = id;
                    const name = parts[i];
                    const link = parts.slice(0, i + 1).join("...");
                    const parent = map[parentPath] || 0;
                    result.push(
                            {
                                id,
                                parent,
                                name,
                                link
                            }                        
                    );
                  
                }
            }
        }
        return result;
    }


}

// Função global necessária pelo HTML existente
function oc(node, bottom) {
    const div = document.getElementById("div" + node);
    div.style.display = div.style.display == "none" ? "" : "none";
}
