from pixiedb import Collections, Collection, Document
import datetime

print("=== 通常の記法（分割記法） / Traditional (Step-by-Step) Style ===")

# ルートコレクション作成
users = Collection("users")

# ドキュメント作成
doc1 = Document({"name": "Alice", "age": 30})

# サブコレクション作成
logs = Collection("logs")
logs.add_document(Document({"action": "login", "time": str(datetime.datetime.now())}))
logs.add_document(Document({"action": "logout", "time": str(datetime.datetime.now())}))

# サブコレクションをドキュメントに追加
doc1.add_subcollection(logs)

# ドキュメントをコレクションに追加
users.add_document(doc1)

# 表示
print(users.documents[0])


print("\n=== メソッドチェイン記法 / Method-Chaining Style ===")

# チェインで同じ構造を作成
users_chain = Collection("users").add_document(
    Document({"name": "Alice", "age": 30})
        .add_subcollection(
            Collection("logs")
                .add_document(Document({"action": "login", "time": str(datetime.datetime.now())}))
                .add_document(Document({"action": "logout", "time": str(datetime.datetime.now())}))
        )
)

# 表示
print(users_chain.documents[0])

# 保存
users.save()
users_chain.save()
