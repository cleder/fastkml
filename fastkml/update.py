from typing import Any, Dict, List, Optional

from fastkml.base import _XMLObject

class Change(_XMLObject):
    
    def __int__(
        self,
        target_id: str,
        elements: List[Dict[str, Any]] = None
    ):
        super.__init__(
            target_id=target_id,
            elements=elements
        )
    
    def parse_children(self):
        pass

class Create(_XMLObject):
    def __init__():
        pass

class Delete(_XMLObject):
    def __init__():
        pass

class Update:

    def __init__(
            target_href: Optional[str] = None,
            change: Optional[Change] = None,
            create: Optional[Create] = None,
            delete: Optional[Delete] = None
    ):
        pass
