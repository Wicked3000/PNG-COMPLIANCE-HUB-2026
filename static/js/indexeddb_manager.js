/**
 * PNG Compliance Hub 2026 — IndexedDB Manager
 * Handles local storage of ledger entries when offline.
 */

const DB_NAME = 'PNGCH_OfflineDB';
const DB_VERSION = 1;
const STORE_NAME = 'offline_ledger';

class IndexedDBManager {
    constructor() {
        this.db = null;
        this.init();
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                console.log('IndexedDB: Database initialized');
                resolve(this.db);
            };

            request.onerror = (event) => {
                console.error('IndexedDB: Initialization error', event.target.error);
                reject(event.target.error);
            };
        });
    }

    async saveEntry(entry) {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.add(entry);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAllEntries() {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readonly');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async deleteEntry(id) {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.delete(id);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async clearAll() {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const store = transaction.objectStore(STORE_NAME);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}

const dbManager = new IndexedDBManager();
window.indexedDBManager = dbManager;
