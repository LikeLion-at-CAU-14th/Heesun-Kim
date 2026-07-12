import os, json, sys, subprocess
from sshtunnel import SSHTunnelForwarder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")

with open(SECRET_FILE) as f:
    secrets = json.load(f)

def get_secret(key):
    try:
        return secrets[key]
    except KeyError:
        raise Exception(f"'{key}' 키 에러")

EC2_HOST = get_secret("EC2_HOST")
EC2_USER = get_secret("EC2_USER")
EC2_KEY_PATH = get_secret("EC2_KEY_PATH")

RDS_HOST = get_secret("RDS_HOST")
RDS_PORT = 3306
LOCAL_PORT = 3307

DB_USER = get_secret("DB_USER")
DB_PW = get_secret("DB_PW")
DB_NAME = "likelion14th"

# 인자로 쿼리 안 주면 테이블 목록 조회
query = sys.argv[1] if len(sys.argv) > 1 else "SHOW TABLES;"

if __name__ == "__main__":
    with SSHTunnelForwarder(
        (EC2_HOST, 22),
        ssh_username=EC2_USER,
        ssh_pkey=EC2_KEY_PATH,
        remote_bind_address=(RDS_HOST, RDS_PORT),
        local_bind_address=('127.0.0.1', LOCAL_PORT),
    ) as tunnel:
        env = os.environ.copy()
        env["MYSQL_PWD"] = DB_PW  # 비밀번호를 커맨드라인 인자 대신 환경변수로 전달

        subprocess.run([
            "mysql",
            "-h", "127.0.0.1",
            "-P", str(LOCAL_PORT),
            "-u", DB_USER,
            DB_NAME,
            "-e", query,
            "--table",
        ], env=env)
