# PyRACLib 存档功能
import os, sys, json
from PyRACLib.log import log

def get_config_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path

class Save:
    def __init__(self):
       self.path = get_config_path()
       self.full = self.path + "/../config.json"
       
       if os.path.exists(self.full) == False:
           with open(self.full, "w") as f:
               f.write("{}")
    
    def write(self, d):
        log.info(f"[Save]: Write {d} -> {self.full}")
        with open(self.full, "w") as f:
            f.write(json.dumps(d))
    
    def read(self, k=None):
        log.info(f"[Save]: Read {self.full} key:{k}")
        with open(self.full, "r") as f:
            res = f.read()
        
        if k != None:
            try:
                res = json.loads(res)
            except:
                return ""
            if k in res:
                return res[k]
            else:
                return ""
        return res