import re
from typing import Optional

def parse_price(s: Optional[str]) -> Optional[float]:
    if s is None: return None
    s = str(s).strip()
    if not s: return None
    s = re.sub(r"[^\d,.\-]", "", s)
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except:
        return None

def to_int_loose(s: Optional[str]) -> int:
    if s is None: return 0
    s = str(s).strip()
    s = s.replace(".", "").replace(",", ".")
    s = re.sub(r"[^\d.]", "", s)
    return int(float(s)) if s else 0

def txt(s: Optional[str]) -> str:
    return (str(s).strip() if s else "")
