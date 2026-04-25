
import csv
from typing import List, Dict, Optional
from config.settings import settings

class IPCBNSMapper:
    def __init__(self):
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> Dict[str, Dict]:
        mapping = {}
        if not settings.IPC_BNS_CSV.exists():
            # Create if not exists with provided default content in build step
            pass 
        
        self.new_offences = []
        try:
            with open(settings.IPC_BNS_CSV, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Capture new offences
                    if row.get("status") == "new_in_bns":
                        self.new_offences.append({
                            "bns_section": row["bns_section"],
                            "description": row["description"],
                            "notes": row["notes"]
                        })

                    # Normalize IPC section key (e.g., "302" -> "302")
                    ipc_sec = row["ipc_section"].strip()
                    if ipc_sec and ipc_sec.lower() != "null":
                        mapping[ipc_sec] = {
                            "bns_section": row["bns_section"],
                            "description": row["description"],
                            "notes": row["notes"]
                        }
        except Exception as e:
            print(f"Error loading mapping CSV: {e}")
            
        return mapping

    def get_new_offences(self) -> List[Dict]:
        """Returns a list of new offences introduced in BNS."""
        return self.new_offences

    def resolve_ipc(self, ipc_section: str) -> Optional[Dict]:
        """
        Returns mapping dict if found, else None.
        ipc_section: e.g. "302", "304A"
        """
        return self.mapping.get(str(ipc_section).strip())

mapper = IPCBNSMapper()
