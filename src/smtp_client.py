import smtplib
import ssl
from typing import Optional
from email.message import EmailMessage
from .config import config
from .logger import logger

class SMTPClient:
    
    def __init__(self , host: str = None , port: int = None, use_tls: bool = True , username: str = None , password: str = None):
        self.host = host or config.SMTP_HOST
        self.port = port or config.SMTP_PORT
        self.use_tls = use_tls if use_tls is not None else config.USE_TLS
        self.username = username or config.SENDER_EMAIL
        self.password = password or config.APP_PASSWORD
        self.server = None
    
    def connect(self):
        logger.info("connecting to smtp server %s %s (use_tls = %s)" , self.host , self.port , self.use_tls)
        
        if self.use_tls and self.port == 465:
            self.server = smtplib.SMTP_SSL(self.host , self.port , context=ssl.create_default_context())
            self.server.ehlo
        else:
            self.server = smtplib.SMTP(self.host , self.port , timeout=60)
            self.server.ehlo
            if self.use_tls:
                ctx = ssl.create_default_context()
                self.server.starttls(context = ctx)
                self.server.ehlo
                
        if self.username and self.password:
            logger.info("Logging in as %s" , self.username)
            self.server.login(self.username , self.password)
        else:
            logger.info("No SMTP credentials provided; attempting anonymous send (may fail)")
        
        
    def send_message(self , message: EmailMessage):
        if self.server is None:
            raise RuntimeError("SMTP client is not connected")
        logger.info("Sending email to %s" , message["To"])
        self.server.send_message(message)
    
    def quit(self):
        if self.server:
            try:
                self.server.quit()
            except Exception:
                try:
                    self.server.close()
                except Exception:
                    pass
        self.server = None
        
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self , exc_type , exc , tb):
        self.quit()
      
    
    