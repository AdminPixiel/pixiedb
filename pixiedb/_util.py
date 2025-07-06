def clean_empty_subcollections(data):
    """再帰的に空のサブコレクションを除去"""
    if isinstance(data, dict):
        if "subcollections" in data:
            cleaned_subs = {}
            for k, v in data["subcollections"].items():
                cleaned = [clean_empty_subcollections(doc) for doc in v]
                # 空ドキュメントは残すが、空のサブコレクションは除去済み
                cleaned = [doc for doc in cleaned if doc.get("subcollections", {}) or doc.get("data")]
                if cleaned:
                    cleaned_subs[k] = cleaned
            if cleaned_subs:
                data["subcollections"] = cleaned_subs
            else:
                data.pop("subcollections")
    return data