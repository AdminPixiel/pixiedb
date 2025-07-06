# PixieDB - Simple Binary NoSQL Database

PixieDBは、シンプルなバイナリ形式のローカルNoSQLデータベースです。  
Firebase Firestoreにインスパイアされ、ローカルファイルに階層的なデータを効率よく保存・読み書きできます。

---

## 📂 データの保存先
コレクションデータは、**プロジェクト内の固定ディレクトリ**に保存されます：

```
./pixiedb_collections/
```

> 初回実行時に自動作成されます。  
> 必要に応じて、保存時に別のディレクトリを指定することも可能です。

---

## 📝 基本的な使い方

### ① データの作成・保存（ルートコレクションのみ）
```python
from pixiedb import Collection, Document

# コレクションとドキュメントを作成
users = Collection("users")
doc = Document({"name": "Alice", "age": 30})
users.add_document(doc)

# サブコレクションも追加可能
logs = Collection("logs")
logs.add_document(Document({"action": "login"}))
doc.add_subcollection(logs)

# ルートコレクションを保存（サブコレクションも自動保存）
users.save()  # ./pixiedb_collections に保存される
```

---

### ② データの読み込み（コレクション単位）

#### ✅ 同名のコレクションをすべて取得
```python
from pixiedb.collections import Collections

users_collections = Collections.find_all_by_name("users")
for col in users_collections:
    print(f"Collection ID: {col.collection_id}, Name: {col.name}")
    for doc in col.documents:
        print(doc.data)
```

#### ✅ 特定のcollection_idでコレクションを取得
```python
target = Collections.get_by_id("users", "abc123")  # IDはファイル名の先頭に記載
print(target.to_list())
```

---

## 💾 保存時の注意
- **サブコレクションは自動保存対象**です。個別保存は不要＆禁止です。
- ルートコレクションだけが `.save()` 可能です。
- 保存ファイル名は自動で生成され、**collection_id** と **コレクション名** が含まれます：
```
abc123_users.bin
```

---

## ✅ 設計のポイント
- **ツリー構造のデータ**をシンプルにローカルで管理
- バイナリ形式で高速＆コンパクト
- Firestoreのような**サブコレクション構造**を簡単に再現
- ファイルはUUID（collection_id）で一意化、複数バージョンも管理可能

---

## 🔧 今後の拡張に備えて
- 将来的に**フィルタ付き読み込み**などにも拡張しやすい設計です。
- ファイル保存先は柔軟に変更可能です。

---

## ✅ まとめ
PixieDBは「**軽量・シンプル・直感的**」を重視したローカルDBです。  
簡単なツールやアプリケーションに最適です。
