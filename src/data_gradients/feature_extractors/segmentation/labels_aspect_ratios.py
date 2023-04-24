import numpy as np

from data_gradients.feature_extractors.feature_extractor_abstract import (
    FeatureExtractorAbstract,
)
from data_gradients.utils import SegBatchData
from data_gradients.utils.data_classes.extractor_results import HistogramResults


class LabelsAspectRatios(FeatureExtractorAbstract):
    def __init__(self):
        super().__init__()
        self._hist = {"train": dict(), "val": dict()}
        self._channels_last = False

    def update(self, data: SegBatchData):
        for label in data.labels:
            ar = np.round(label.shape[2] / label.shape[1], 2)
            if ar not in self._hist[data.split]:
                self._hist[data.split][ar] = 1
            else:
                self._hist[data.split][ar] += 1

    def _aggregate(self, split: str):
        self.merge_dict_splits(self._hist)
        values = list(self._hist[split].values())
        bins = list(self._hist[split].keys())

        results = HistogramResults(
            bin_names=bins,
            bin_values=values,
            plot="bar-plot",
            split=split,
            color=self.colors[split],
            title="Labels aspect ratios",
            x_label="Aspect ratio [W / H]",
            y_label="# Of Labels",
            ticks_rotation=0,
            y_ticks=True,
        )
        return results
