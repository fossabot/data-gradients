from data_gradients.feature_extractors.feature_extractor_abstract import (
    FeatureExtractorAbstract,
)
from data_gradients.utils import BatchData
from data_gradients.utils.data_classes.extractor_results import HistoResults


class ImagesResolutions(FeatureExtractorAbstract):
    def __init__(self):
        super().__init__()
        self._hist = {"train": dict(), "val": dict()}

    def update(self, data: BatchData):
        for image in data.images:
            res = str(tuple((image.shape[2], image.shape[1])))
            if res not in self._hist[data.split]:
                self._hist[data.split][res] = 1
            else:
                self._hist[data.split][res] += 1

    def aggregate_to_result_dict(self, split: str):
        values, bins = self.aggregate(split)
        results = HistoResults(
            bins=bins,
            values=values,
            plot="bar-plot",
            split=split,
            color=self.colors[split],
            title="Image resolutions",
            x_label="Resolution [W, H]",
            y_label="# Of Images",
            ticks_rotation=0,
            y_ticks=True,
        )
        return results

    def aggregate(self, split: str):
        self.merge_dict_splits(self._hist)
        values = list(self._hist[split].values())
        bins = list(self._hist[split].keys())
        return values, bins
