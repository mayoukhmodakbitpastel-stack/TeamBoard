import hashlib

def md5_hash_project_id(project_id: int) -> str:
    return hashlib.md5(f"project_{project_id}".encode()).hexdigest()

def md5_decode_project_id(hash_id: str, model) -> int:
    # This function finds the numeric ID by comparing hashes with prefix "project_"
    for obj in model.objects.all():
        if md5_hash_project_id(obj.id) == hash_id:
            return obj.id
    return None
# hash message id
def md5_hash_message_id(message_id: int) -> str:
    return hashlib.md5(f"message_{message_id}".encode()).hexdigest()