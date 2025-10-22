from hashids import Hashids

HASHIDS_SALT="kdbd94adfvb451df4fregeb51dbry4hry8jutk8iykuj1m5yikl8iy4k1dy5iklyid84k1myu4tu8j5y1fkx8ut4k"

MIN_HASH_LENGTH= 8
hashids=Hashids(salt=HASHIDS_SALT,min_length=MIN_HASH_LENGTH)

def encode_id(raw_id):
    return hashids.encode(raw_id)

def decode_id(hash_id):
    decoded = hashids.decode(hash_id)
    return decoded[0] if decoded else None
