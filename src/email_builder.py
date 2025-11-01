from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
import mimetypes
from typing import List , Optional
from .template_renderer import render_template
from .logger import logger

def parse_attachment_parts(field_value: Optional[str]) -> List[str]:
    if not field_value:
        return
    parts = [p.strip() for p in field_value.split(";") if p.strip()] 
    return parts

def build_message(sender: str , recipients_row: dict) -> EmailMessage:
    to_addr = recipients_row.get("email")
    if not to_addr:
        raise ValueError("Recipient row missing 'email' field")
    
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    subject = recipients_row.get("subject") or f"Hello {recipients_row.get('name','')}"
    msg["Subject"] = subject
    
    attach_field = recipients_row.get("attachment_paths" , "")
    paths = parse_attachment_parts(attach_field)
    
    if not paths:
        paths = []
    
    for p in paths:
        ppath = Path(p)
        if not ppath.exists():
            logger.warning("Attachments not found. Skipping %s" , p)
            continue
        
        ctype, encoding = mimetypes.guess_type(str(ppath))
        if ctype is None:
            maintype, subtype = ("application", "octet-stream")
        else:
            maintype, subtype = ctype.split("/", 1)
        with ppath.open("rb") as f:
            data = f.read()
        # attach
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=ppath.name)

    return msg