import random
import string

def random_string(length=32):    
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
