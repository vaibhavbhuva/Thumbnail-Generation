from abc import ABC, abstractmethod
from typing import Union, Optional

class Storage(ABC):
    @abstractmethod
    def write_file(
        self,
        file_path: str,
        file_content: Union[str, bytes],
        mime_type: Optional[str] = None,
    ):
        """
        Write file to internal storage
        """

    @abstractmethod
    def public_url(self, file_path: str) -> str:
        """
        Make Public URL
        """