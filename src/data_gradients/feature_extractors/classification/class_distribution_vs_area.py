import numpy as np
import pandas as pd

from data_gradients.common.registry.registry import register_feature_extractor
from data_gradients.feature_extractors.abstract_feature_extractor import Feature
from data_gradients.utils.data_classes.data_samples import ClassificationSample
from data_gradients.visualize.plot_options import ViolinPlotOptions
from data_gradients.feature_extractors.abstract_feature_extractor import AbstractFeatureExtractor


@register_feature_extractor()
class ClassificationClassDistributionVsArea(AbstractFeatureExtractor):
    """
    Summarizes how average image dimensions vary among classes and data splits.

    This feature extractor calculates the mean image size (width and height) for each label within the provided splits of the dataset.
    It highlights potential discrepancies in image resolutions across different classes and dataset splits, which could impact model performance.
    Disparities in image sizes could indicate a need for more uniform data collection or preprocessing to avoid model biases and ensure consistent
    performance across all classes and splits.

    Key Uses:

    - Pinpointing classes with significant variations in image resolution to inform data collection and preprocessing.
    - Assessing the consistency of image resolutions across dataset splits to guide training strategies and augmentation techniques.
    """

    def __init__(self):
        self.data = []

    def update(self, sample: ClassificationSample):
        class_name = sample.class_names[sample.class_id]
        self.data.append(
            {
                "split": sample.split,
                "class_id": sample.class_id,
                "class_name": class_name,
                "image_size": int(np.sum(sample.image.shape[:2]) // 2),
            }
        )

    def aggregate(self) -> Feature:
        df = pd.DataFrame(self.data)

        all_class_names = df["class_name"].unique()

        num_splits = len(df["split"].unique())
        # Height of the plot is proportional to the number of classes
        n_unique = len(all_class_names)
        figsize_x = 10
        figsize_y = min(max(6, int(n_unique * 0.3)), 175)

        plot_options = ViolinPlotOptions(
            x_label_key="image_size",
            x_label_name="Image size (px)",
            y_label_key="class_name",
            y_label_name="Class",
            order_key="class_id",
            figsize=(figsize_x, figsize_y),
            x_ticks_rotation=None,
            labels_key="split" if num_splits > 1 else None,
            tight_layout=True,
        )

        df_summary = df[["split", "class_name", "image_size"]].groupby(["split", "class_name", "image_size"]).size().reset_index(name="counts")

        json = df_summary.to_dict(orient="records")

        feature = Feature(
            data=df,
            plot_options=plot_options,
            json=json,
            title="Image size distribution per class",
            description=(
                "Distribution of image size (mean value of image width & height) with respect to assigned image label and (when possible) a split.\n"
                "This may highlight issues when classes in train/val has different image resolution which may negatively affect the accuracy of the model.\n"
                "If you see a large difference in image size between classes and splits - you may need to adjust data collection process or training regime:\n"
                " - When splitting data into train/val/test - make sure that the image size distribution is similar between splits.\n"
                " - If size distribution overlap between splits to too big - "
                "you can address this (to some extent) by using more agressize values for zoom-in/zoo-out augmentation at training time.\n"
            ),
        )
        return feature
