import uuid
import struct
from ._binary_codec import encode_value, decode_value
from ._util import clean_empty_subcollections
import os
from typing import Callable

DEFAULT_DIR = "./.pixiedb_collections"  # データ保存ディレクトリ（固定）

class Document:
    def __init__(self, doc_id=None, data=None):
        self.id = doc_id or str(uuid.uuid4())
        self.data = data or {}
        self.subcollections = {}

    def add_subcollection(self, collection):
        collection._parent = self  # 親ドキュメントをセット
        self.subcollections[collection.name] = collection
        return self #メソッドチェーン可能に

    def to_bytes(self):
        encoded_data = encode_value(self.data)
        sub_bytes = struct.pack('I', len(self.subcollections))
        for name, collection in self.subcollections.items():
            encoded_name = name.encode('utf-8')
            sub_bytes += struct.pack('I', len(encoded_name)) + encoded_name
            sub_bytes += collection.to_bytes()
        return encoded_data + sub_bytes

    def to_dict(self):
        '''Documentを`dict`に展開'''
        return {
            "id":self.id,
            "data": self.data,
            "subcollections": {name: col.to_list() for name, col in self.subcollections.items()}
        }
    
    def __repr__(self):
        # 元のdictから、空のサブコレクションを除外
        d = self.to_dict()
        cleaned = clean_empty_subcollections(d)
        return f"Document({cleaned})"

    @staticmethod
    def from_bytes(data_bytes):
        offset = 0
        data, used = decode_value(data_bytes[offset:])
        offset += used
        doc = Document(data)
        sub_collections_count = struct.unpack('I', data_bytes[offset:offset+4])[0]
        offset += 4
        for _ in range(sub_collections_count):
            name_len = struct.unpack('I', data_bytes[offset:offset+4])[0]
            offset += 4
            name = data_bytes[offset:offset+name_len].decode('utf-8')
            offset += name_len
            collection, used = Collection.from_bytes_with_offset(data_bytes[offset:])
            collection.name = name
            doc.add_subcollection(collection)  # ここで親セット
            offset += used
        return doc, offset

class Collection:
    def __init__(self, name, collection_id=None):
        self.name = name
        self.id = collection_id or str(uuid.uuid4())
        self.documents = []
        self._parent = None  # 親を持たない（ルート）

    def add_document(self, document):
        self.documents.append(document)
        return self #メソッドチェーン可能に

    def get_documents(self, condition: Callable[[Document], bool]=lambda doc: True):
        """
        ### 条件に一致するドキュメントを取得
        arg: condition (Callable [ [ Document ], bool ], optional): 各ドキュメントを受け取り、条件を判定して真偽値を返す関数

        return: `list[Document]`: 条件に一致するドキュメントのリスト
        """
        return [doc for doc in self.documents if condition(doc)]

    def get_document_by_id(self, doc_id: str):
        """指定IDのドキュメントを取得（なければNone）"""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None

    def find_first(self, condition):
        """
        ### 条件に一致するドキュメントの最初の一つ目を取得
        arg: condition (Callable [ [ Document ], bool ], optional): 各ドキュメントを受け取り、条件を判定して真偽値を返す関数

        return: `Document` or `None`: 条件に一致する最初のドキュメント
        """
        docs = self.get_documents(condition=condition)
        if docs:
            return docs[0]
        return None

    def has_document(self, condition):
        """
        ### 条件に一致するドキュメントの存在確認
        arg: condition (Callable [ [ Document ], bool ], optional): 各ドキュメントを受け取り、条件を判定して真偽値を返す関数

        return: `bool`: 一つでも存在すればTrue
        """
        return any(condition(doc) for doc in self.documents)

    def to_bytes(self):
        result = struct.pack('I', len(self.documents))
        for doc in self.documents:
            doc_bytes = doc.to_bytes()
            result += struct.pack('I', len(doc_bytes)) + doc_bytes
        return result
    
    def to_list(self):
        '''Collectionを`list`に展開'''
        return [doc.to_dict() for doc in self.documents]

    def __repr__(self):
        return f'Collection(name="{self.name}", documents={self.to_list()})'

    @classmethod
    def from_bytes_with_offset(cls, data_bytes):
        offset = 0
        doc_count = struct.unpack('I', data_bytes[offset:offset+4])[0]
        offset += 4
        collection = cls("unknown")
        for _ in range(doc_count):
            doc_len = struct.unpack('I', data_bytes[offset:offset+4])[0]
            offset += 4
            doc_data = data_bytes[offset:offset+doc_len]
            offset += doc_len
            doc, _ = Document.from_bytes(doc_data)
            collection.add_document(doc)
        return collection, offset

    def save(self, directory=None):
        """ルートコレクションだけが保存可能"""
        base_dir = directory or DEFAULT_DIR
        if self._parent is not None:
            raise RuntimeError("サブコレクションの保存は禁止されています。ルートコレクションのみ保存可能です。")
        filename = f"{self.collection_id}_{self.name}.bin"
        filepath = f"{base_dir}/{filename}"
        with open(filepath, 'wb') as f:
            f.write(self.to_bytes())
        print(f"Saved to {filepath}")

    @classmethod
    def load_from_file(cls, filename):
        """ファイルからコレクションを読み込む"""
        with open(filename, 'rb') as f:
            data = f.read()
        collection, _ = cls.from_bytes_with_offset(data)
        # ファイル名からIDと名前を推測
        basename = filename.split('/')[-1].replace('.bin', '')
        parts = basename.split('_', 1)
        if len(parts) == 2:
            collection.collection_id, collection.name = parts
        collection._parent = None  # ルートコレクションとして読み込み
        return collection


class Collections:
    """Collection Utility"""

    @staticmethod
    def _load_collections(collection_name, base_dir=None):
        """内部共通：同名コレクションをすべて読み込む"""
        base_dir = base_dir or DEFAULT_DIR
        collections = []
        for filename in os.listdir(base_dir):
            if filename.endswith(f"_{collection_name}.bin"):
                filepath = os.path.join(base_dir, filename)
                col = Collection.load_from_file(filepath)
                collections.append(col)
        return collections

    @staticmethod
    def find_all_by_name(collection_name, base_dir=None):
        """指定されたコレクション名のコレクションをすべて探して読み込む"""
        return Collections._load_collections(collection_name, base_dir)

    @staticmethod
    def get_by_id(collection_name, collection_id, base_dir=None):
        """特定のcollection_idを持つコレクションを取得"""
        collections = Collections._load_collections(collection_name, base_dir)
        for col in collections:
            if col.id == collection_id:
                return col
        raise ValueError(f"Collection with ID '{collection_id}' not found in '{collection_name}'")
    