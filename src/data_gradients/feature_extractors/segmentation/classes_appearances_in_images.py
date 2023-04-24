import torch

from data_gradients.logging.logger_utils import class_id_to_name
from data_gradients.utils import SegmentationBatchData
from data_gradients.feature_extractors.feature_extractor_abstract import (
    FeatureExtractorAbstract,
)
from data_gradients.utils.data_classes.extractor_results import HistogramResults


class AppearancesInImages(FeatureExtractorAbstract):
    """
    Semantic Segmentation task feature extractor -
    For each class, calculate percentage of images it appears in out of all images in set.
    """

    def __init__(self, num_classes, ignore_labels):
        super().__init__()
        self.ignore_labels = ignore_labels
        keys = [int(i) for i in range(0, num_classes + len(ignore_labels)) if i not in ignore_labels]
        self._hist = {"train": dict.fromkeys(keys, 0), "val": dict.fromkeys(keys, 0)}
        self._number_of_images = {"train": 0, "val": 0}

    def update(self, data: SegmentationBatchData):
        self._number_of_images[data.split] += len(data.labels)
        for i, label in enumerate(data.labels):
            for j, class_channel in enumerate(label):
                if torch.max(class_channel) > 0:
                    self._hist[data.split][j] += 1

    def _aggregate(self, split: str):
        self._hist[split] = class_id_to_name(self.id_to_name, self._hist[split])
        values = self.normalize(self._hist[split].values(), self._number_of_images[split])
        bins = self._hist[split].keys()

        results = HistogramResults(
            bin_names=bins,
            bin_values=values,
            plot="bar-plot",
            split=split,
            color=self.colors[split],
            title="% Images that class appears in",
            x_label="Class #",
            y_label="Images appeared in [%]",
            y_ticks=True,
            ax_grid=True,
        )
        return results
