import logging
import sys
from pathlib import Path

LOG_FILE = Path("send.log")

def setup_logging():
    
    with open ("send.log" , "w"):
        pass
    
    logger = logging.getLogger("email_automation_tool")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        
        # console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        logger.addHandler(ch) 
        
        #file handler
        fh = logging.FileHandler(LOG_FILE , encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        
    return logger

logger = setup_logging() 

         