import random, string, secrets, re, json
from fastapi import HTTPException

class CustomError(HTTPException):
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)
        self.message = message

def generate_random_string(size=32): return "".join([random.choice(string.ascii_letters + string.digits) for n in range(size)])
def generate_ver_token(): return "ver_token_" + generate_random_string(128)
def generate_user_id(): return "na_usr_" + generate_random_string(20)
def generate_thread_id(): return generate_random_string(20)
def generate_random_number(size=6): return "".join(["{}".format(random.randint(0, 9)) for num in range(size)])
def generate_api_key(): return "na-sk-" + secrets.token_urlsafe(64)

def extract_json(raw: str):
    try:
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw: raw = raw.split("```")[1].split("```")[0]
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw.strip())
    except Exception as e: raise ValueError(f"Failed to parse JSON: {e}")

def extract_json_array(raw: str):
    try:
        if "```json" in raw: raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw: raw = raw.split("```")[1].split("```")[0]
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(raw.strip())
    except Exception as e: raise ValueError(f"Failed to parse JSON array: {e}")
