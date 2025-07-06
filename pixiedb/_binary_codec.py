import struct
import datetime

def encode_value(value):
    """値を型付きバイナリにエンコード"""
    if isinstance(value, int):
        type_id = 1
        data = struct.pack('q', value)
    elif isinstance(value, float):
        type_id = 2
        data = struct.pack('d', value)
    elif isinstance(value, str):
        type_id = 3
        encoded = value.encode('utf-8')
        data = struct.pack('I', len(encoded)) + encoded
    elif isinstance(value, bool):
        type_id = 4
        data = struct.pack('B', 1 if value else 0)
    elif isinstance(value, datetime.datetime):
        type_id = 5
        dt = value.astimezone(datetime.timezone.utc)
        seconds = int(dt.timestamp())
        nanoseconds = int((dt.timestamp() - seconds) * 1_000_000_000)
        data = struct.pack('qI', seconds, nanoseconds)
    elif isinstance(value, list):
        type_id = 7
        elements = b''.join(encode_value(item) for item in value)
        data = struct.pack('I', len(value)) + elements
    elif isinstance(value, dict):
        type_id = 8
        pairs = b''
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("Map keys must be strings")
            encoded_key = k.encode('utf-8')
            key_data = struct.pack('I', len(encoded_key)) + encoded_key
            value_data = encode_value(v)
            pairs += key_data + value_data
        data = struct.pack('I', len(value)) + pairs
    else:
        raise ValueError('Unsupported type')

    return struct.pack('B', type_id) + data

def decode_value(data):
    """型付きバイナリをデコード"""
    type_id = struct.unpack('B', data[0:1])[0]
    offset = 1

    if type_id == 1:
        value = struct.unpack('q', data[offset:offset+8])[0]
        offset += 8
    elif type_id == 2:
        value = struct.unpack('d', data[offset:offset+8])[0]
        offset += 8
    elif type_id == 3:
        str_len = struct.unpack('I', data[offset:offset+4])[0]
        offset += 4
        value = data[offset:offset+str_len].decode('utf-8')
        offset += str_len
    elif type_id == 4:
        value = struct.unpack('B', data[offset:offset+1])[0] == 1
        offset += 1
    elif type_id == 5:
        seconds, nanoseconds = struct.unpack('qI', data[offset:offset+12])
        offset += 12
        timestamp = seconds + nanoseconds / 1_000_000_000
        value = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    elif type_id == 7:
        list_len = struct.unpack('I', data[offset:offset+4])[0]
        offset += 4
        value = []
        for _ in range(list_len):
            item, used = decode_value(data[offset:])
            value.append(item)
            offset += used
    elif type_id == 8:
        pair_len = struct.unpack('I', data[offset:offset+4])[0]
        offset += 4
        value = {}
        for _ in range(pair_len):
            key_len = struct.unpack('I', data[offset:offset+4])[0]
            offset += 4
            key = data[offset:offset+key_len].decode('utf-8')
            offset += key_len
            val, used = decode_value(data[offset:])
            value[key] = val
            offset += used
    else:
        raise ValueError('Unknown type ID')

    return value, offset

# --- デモ ---
# values = [
#     {"name": "Alice", "age": 30, "languages": ["Python", "C++"]},
#     {"numbers": [1, 2, 3], "nested": {"flag": True, "score": 99.9}},
# ]

# # エンコードしてファイル保存
# with open('db_map.bin', 'wb') as f:
#     for v in values:
#         f.write(encode_value(v))

# # 読み込み＆デコード
# with open('db_map.bin', 'rb') as f:
#     data = f.read()

# offset = 0
# while offset < len(data):
#     value, used = decode_value(data[offset:])
#     print(f'読み取った値: {value}')
#     offset += used