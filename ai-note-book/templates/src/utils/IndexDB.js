export default class IndexedDBUtil {
    constructor(dbName, storeName) {
        this.dbName = dbName;
        this.storeName = storeName;
        this.db = null;
        this.initDB();
    }

    // 打开并初始化数据库
    initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);

            request.onupgradeneeded = event => {
                this.db = event.target.result;
                if (!this.db.objectStoreNames.contains(this.storeName)) {
                    const objectStore = this.db.createObjectStore(this.storeName, { keyPath: 'id', autoIncrement: true });
                    objectStore.createIndex('name', 'name', { unique: false });
                }
            };

            request.onsuccess = event => {
                this.db = event.target.result;
                resolve();
            };

            request.onerror = event => {
                console.error('打开数据库失败:', event.target.error);
                reject(event.target.error);
            };
        });
    }

    // 增加记录
    add(data) {
        return this.initDB().then(() => {
            return new Promise((resolve, reject) => {
                const transaction = this.db.transaction([this.storeName], 'readwrite');
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.add(data);

                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            });
        });
    }

    // 根据 ID 获取记录
    getById(id) {
        return this.initDB().then(() => {
            return new Promise((resolve, reject) => {
                const transaction = this.db.transaction([this.storeName]);
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.get(id);

                request.onsuccess = () => {
                    if (request.result) {
                        resolve(request.result);
                    } else {
                        console.warn(`未找到 ID 为 ${id} 的记录`); // 输出警告信息
                        resolve(null); // No result found
                    }
                };

                request.onerror = () => {
                    console.error('获取记录失败:', request.error); // 输出错误信息
                    reject(request.error);
                };
            });
        });
    }

    // 获取所有记录
    getAll() {
        return this.initDB().then(() => {
            return new Promise((resolve, reject) => {
                const transaction = this.db.transaction([this.storeName]);
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.getAll();

                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            });
        });
    }

    // 根据 ID 更新记录
    update(data) {
        return this.initDB().then(() => {
            return new Promise((resolve, reject) => {
                const transaction = this.db.transaction([this.storeName], 'readwrite');
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.put(data);

                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            });
        });
    }

    // 根据 ID 删除记录
    delete(id) {
        return this.initDB().then(() => {
            return new Promise((resolve, reject) => {
                const transaction = this.db.transaction([this.storeName], 'readwrite');
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.delete(id);

                request.onsuccess = () => resolve();
                request.onerror = () => reject(request.error);
            });
        });
    }

    // 清空对象存储中的所有记录
    clearAll() {
        return this.initDB().then(() => {
            return new Promise((resolve, reject) => {
                const transaction = this.db.transaction([this.storeName], 'readwrite');
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.clear();

                request.onsuccess = () => resolve();
                request.onerror = () => reject(request.error);
            });
        });
    }

    // 删除整个数据库
    deleteDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.deleteDatabase(this.dbName);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
            request.onblocked = () => console.warn('删除数据库请求被阻塞');
        });
    }
}

