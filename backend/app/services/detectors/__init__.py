from app.services.detectors.class_imbalance import ClassImbalanceDetector
from app.services.detectors.data_leakage import DataLeakageDetector
from app.services.detectors.duplicates import DuplicateDetector, NearDuplicateDetector
from app.services.detectors.missing_values import MissingValuesDetector
from app.services.detectors.outliers import OutlierDetector

ALL_DETECTORS = [
    MissingValuesDetector(),
    DuplicateDetector(),
    NearDuplicateDetector(),
    OutlierDetector(),
    ClassImbalanceDetector(),
    DataLeakageDetector(),
]
