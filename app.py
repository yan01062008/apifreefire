import asyncio
import time
import httpx
import json
import os
import random
from collections import defaultdict
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Tuple

from proto import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
from google.protobuf import json_format, message
from google.protobuf.message import Message

try:
    from cachetools import TTLCache
    cache = TTLCache(maxsize=300, ttl=300)
except Exception:
    cache = {}

try:
    from Crypto.Cipher import AES
    def pad_bytes(text: bytes) -> bytes:
        padding_length = AES.block_size - (len(text) % AES.block_size)
        return text + bytes([padding_length] * padding_length)

    def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
        aes = AES.new(key, AES.MODE_CBC, iv)
        return aes.encrypt(pad_bytes(plaintext))
except ImportError:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    def pad_bytes(text: bytes) -> bytes:
        pad_len = 16 - (len(text) % 16)
        return text + bytes([pad_len] * pad_len)

    def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        enc = cipher.encryptor()
        return enc.update(pad_bytes(plaintext)) + enc.finalize()

# === Cấu hình Hệ thống ===
MAIN_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])  # b'Yg&tc%DEuh6%Zc^8'
MAIN_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])  # b'6oyZDr22E3ychjM%'
RELEASEVERSION = "OB49"
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
SUPPORTED_REGIONS = {"IND", "BR", "US", "SAC", "NA", "SG", "RU", "ID", "TW", "VN", "TH", "ME", "PK", "CIS", "BD", "EUROPE"}

# === Khởi tạo Flask ===
app = Flask(__name__)
CORS(app)
cached_tokens = defaultdict(dict)

# === Helper Protobuf ===
def decode_protobuf(encoded_data: bytes, message_type: message.Message) -> message.Message:
    instance = message_type()
    instance.ParseFromString(encoded_data)
    return instance

async def json_to_proto(json_data: str, proto_message: Message) -> bytes:
    json_format.ParseDict(json.loads(json_data), proto_message)
    return proto_message.SerializeToString()

def get_account_credentials(region: str) -> str:
    r = (region or "VN").strip().upper()
    if r == "IND":
        return "uid=3692279677&password=473AFFEF67F708CBB0962A958BB2809DA0843EA41BDB70D738FD9527EA04B27B"
    elif r in {"BR", "US", "SAC", "NA"}:
        return "uid=3692292847&password=FC22F6812C850FF7D8DB8C5474A106B6FE22CB10C0A6673837216A32675E5649"
    elif r == "VN":
        return "uid=3686689562&password=AD9C4A2B51A749481913F72A36F68A9F231520E9AC29B244DB47A64FD7353A12"
    elif r == "SG":
        return "uid=3692265171&password=A2A5E3C252A35B2BB30698BD1469A759417A68A069CF6980ED959EB01D352E28"
    elif r == "ID":
        return "uid=3692307512&password=4AA06E1DB3F998ABDBDA74578D26B0C84700EC5C079751E7C8F1626048DDBCAE"
    elif r == "TH":
        return "uid=3692333198&password=0ED64C5A89E09B8BE538829B0304FE5F5F7EA3BBE645A341C73ECA49143D2211"
    elif r == "TW":
        return "uid=3692312456&password=1A062FD700DA8F826AF84A37EE2B62121B79516AF71666949C72FFF42D1C554A"
    else:
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            acc_path = os.path.join(base_dir, "accounts.txt")
            if os.path.exists(acc_path):
                with open(acc_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    if lines:
                        uid, password = random.choice(lines).split()
                        return f"uid={uid}&password={password}"
        except Exception:
            pass
        return "uid=3686689562&password=AD9C4A2B51A749481913F72A36F68A9F231520E9AC29B244DB47A64FD7353A12"

# === Token Generation ===
async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = account + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.post(url, data=payload, headers=headers)
        data = resp.json()
        return data.get("access_token", "0"), data.get("open_id", "0")

async def create_jwt(region: str):
    account = get_account_credentials(region)
    token_val, open_id = await get_access_token(account)
    body = json.dumps({"open_id": open_id, "open_id_type": "4", "login_token": token_val, "orign_platform_type": "4"})
    proto_bytes = await json_to_proto(body, FreeFire_pb2.LoginReq())
    payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': RELEASEVERSION
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, data=payload, headers=headers)
        msg = json.loads(json_format.MessageToJson(decode_protobuf(resp.content, FreeFire_pb2.LoginRes)))
        cached_tokens[region] = {
            'token': f"Bearer {msg.get('token','0')}",
            'region': msg.get('lockRegion','0'),
            'server_url': msg.get('serverUrl','0'),
            'expires_at': time.time() + 25200
        }

async def get_token_info(region: str) -> Tuple[str,str,str]:
    info = cached_tokens.get(region)
    if info and time.time() < info.get('expires_at', 0):
        return info['token'], info['region'], info['server_url']
    await create_jwt(region)
    info = cached_tokens[region]
    return info['token'], info['region'], info['server_url']

async def GetAccountInformation(uid: str, unk: str, region: str, endpoint: str):
    region = (region or "VN").upper()
    if region not in SUPPORTED_REGIONS:
        region = "VN"
    payload = await json_to_proto(json.dumps({'a': str(uid), 'b': str(unk)}), main_pb2.GetPlayerPersonalShow())
    data_enc = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, payload)
    token, lock, server = await get_token_info(region)
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'Authorization': token,
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': RELEASEVERSION
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(server + endpoint, data=data_enc, headers=headers)
        parsed = decode_protobuf(resp.content, AccountPersonalShow_pb2.AccountPersonalShowInfo)
        res_dict = json.loads(json_format.MessageToJson(parsed))
        res_dict["uid"] = str(uid)
        return res_dict

# === Decorator Caching ===
def cached_endpoint(ttl=300):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **k):
            key = (request.path, tuple(sorted(request.args.items())))
            if isinstance(cache, dict) and key in cache:
                return cache[key]
            res = fn(*a, **k)
            if isinstance(cache, dict):
                cache[key] = res
            return res
        return wrapper
    return decorator

# === Các Routes API ===

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Hệ Thống API Tra Cứu Free Fire & Anti-Cheat",
        "credits": "Yan Dev",
        "endpoints": {
            "easy": "/info?uid={uid}",
            "multi_region": "/player-info?region={region}&uid={uid}",
            "compatible": "/api/freefire/info?uid={uid}"
        },
        "supported_regions": sorted(list(SUPPORTED_REGIONS)),
        "example": "/info?uid=1154264866"
    }), 200

@app.route('/info')
@app.route('/player-info')
@app.route('/api/freefire/info')
@cached_endpoint()
def get_player_info():
    uid = request.args.get('uid', '').strip()
    region = request.args.get('region', 'VN').strip().upper()

    if not uid:
        return jsonify({"error": "Vui lòng nhập UID người chơi (?uid=...)"}), 400

    clean_uid = "".join([c for c in uid if c.isdigit()])
    if not clean_uid or len(clean_uid) < 5:
        return jsonify({"error": "UID không hợp lệ. Vui lòng nhập ít nhất 5 chữ số."}), 400

    if region not in SUPPORTED_REGIONS:
        region = "VN"

    try:
        return_data = asyncio.run(GetAccountInformation(clean_uid, "7", region, "/GetPlayerPersonalShow"))
        return jsonify(return_data), 200
    except Exception as e:
        return jsonify({
            "error": "Không thể lấy thông tin tài khoản Free Fire từ Garena.",
            "details": str(e),
            "uid": clean_uid,
            "region": region
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
