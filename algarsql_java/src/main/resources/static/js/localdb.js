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