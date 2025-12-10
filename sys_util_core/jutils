import re
from typing import Optional

class ErrorTextUtils(Exception): pass
class TextUtils:
    @staticmethod
    def extract_version(version_check: str, num_of_pt: int = 2) -> Optional[str]:
        num_of_pt = max(1, min(num_of_pt, 6))
        version_patterns = [
            r"\d+\.\d+\.\d+\.\d+\.\d+\.\d+",    # x.y.z.w.v.u
            r"\d+\.\d+\.\d+\.\d+\.\d+",         # x.y.z.w.v
            r"\d+\.\d+\.\d+\.\d+",              # x.y.z.w
            r"\d+\.\d+\.\d+",                   # x.y.z
            r"\d+\.\d+"                         # x.y
        ]
        for pattern in version_patterns[-num_of_pt:]:
            match = re.search(pattern, version_check)
            if match:
                return match.group()
        return None