import subprocess
from para import EXP_EXECUTE_TIME

for i in range(0, EXP_EXECUTE_TIME):
    print(f">>> Run {i+1}-th... ")

    # excute: python3.10 main.py
    result = subprocess.run(['python3.10', 'main.py'])
    if result.stderr:
        print(f"[ERROR]：{result.stderr}")  

print(f" [SUCCEED] ")
        

