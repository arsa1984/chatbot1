# D:\ArsaWebDeveloper\Project\Vexta\auth\utils.py
import random

def generate_otp() -> str:
    return str(random.randint(10000, 99999))
