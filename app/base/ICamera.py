from abc import ABC, abstractmethod
from datetime import datetime


class ICamera(ABC):
    @abstractmethod
    def get_current_time(self) -> datetime: ...
    
    @abstractmethod
    def track_video(self) -> dict: ...
