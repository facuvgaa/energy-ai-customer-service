from dataclasses import dataclass

@dataclass
class Command:
    session_id: str
    user_id: str
    content: str