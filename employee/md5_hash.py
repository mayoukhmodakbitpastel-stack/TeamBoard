import hashlib

def md5_hash_id(raw_id: int) -> str:
    return hashlib.md5(str(raw_id).encode()).hexdigest()

def md5_decode_id(hash_id: str, model) -> int:
    for obj in model.objects.all():
        if md5_hash_id(obj.id) == hash_id:
            return obj.id
    return None

