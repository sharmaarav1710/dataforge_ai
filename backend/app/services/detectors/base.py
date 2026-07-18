from abc import ABC, abstractmethod

import pandas as pd

from app.schemas.issues import DetectedIssue


class BaseDetector(ABC):
    name: str

    @abstractmethod
    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        pass
