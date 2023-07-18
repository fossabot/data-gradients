from typing import Optional, Iterable, Callable, List

import torch

from data_gradients.batch_processors.detection import DetectionBatchProcessor
from data_gradients.config.data.data_config import DetectionDataConfig
from data_gradients.config.data.typing import SupportedDataType, FeatureExtractorsType
from data_gradients.config.utils import get_grouped_feature_extractors
from data_gradients.managers.abstract_manager import AnalysisManagerAbstract


class DetectionAnalysisManager(AnalysisManagerAbstract):
    """Main detection manager class.
    Definition of task name, task-related preprocessor and parsing related configuration file
    """

    def __init__(
        self,
        *,
        report_title: str,
        train_data: Iterable[SupportedDataType],
        val_data: Iterable[SupportedDataType],
        report_subtitle: Optional[str] = None,
        config_path: Optional[str] = None,
        feature_extractors: Optional[FeatureExtractorsType] = None,
        log_dir: Optional[str] = None,
        use_cache: bool = False,
        class_names: Optional[List[str]] = None,
        class_names_to_use: Optional[List[str]] = None,
        n_classes: Optional[int] = None,
        images_extractor: Optional[Callable[[SupportedDataType], torch.Tensor]] = None,
        labels_extractor: Optional[Callable[[SupportedDataType], torch.Tensor]] = None,
        is_label_first: Optional[bool] = None,
        bbox_format: Optional[str] = None,
        n_image_channels: int = 3,
        batches_early_stop: Optional[int] = None,
        remove_plots_after_report: Optional[bool] = True,
    ):
        """
        Constructor of detection manager which controls the analyzer
        :param report_title:            Title of the report. Will be used to save the report
        :param report_subtitle:         Subtitle of the report
        :param class_names:             List of all class names in the dataset. The index should represent the class_id.
        :param class_names_to_use:      List of class names that we should use for analysis.
        :param n_classes:               Number of classes. Mutually exclusive with `class_names`.
        :param train_data:              Iterable object contains images and labels of the training dataset
        :param val_data:                Iterable object contains images and labels of the validation dataset
        :param config_path:             Full path the hydra configuration file. If None, the default configuration will be used. Mutually exclusive
                                        with feature_extractors
        :param feature_extractors:      One or more feature extractors to use. If None, the default configuration will be used. Mutually exclusive
                                        with config_path
        :param log_dir:                 Directory where to save the logs. By default uses the current working directory
        :param batches_early_stop:      Maximum number of batches to run in training (early stop)
        :param use_cache:               Whether to use cache or not for the configuration of the data.
        :param images_extractor:        Function extracting the image(s) out of the data output.
        :param labels_extractor:        Function extracting the label(s) out of the data output.
        :param is_label_first:          Whether the labels are in the first dimension or not.
                                            > (class_id, x, y, w, h) for instance, as opposed to (x, y, w, h, class_id)
        :param bbox_format:             Format of the bounding boxes. 'xyxy', 'xywh' or 'cxcywh'
        :param n_image_channels:        Number of channels for each image in the dataset
        :param remove_plots_after_report:  Delete the plots from the report directory after the report is generated. By default, True
        """
        if feature_extractors is not None and config_path is not None:
            raise RuntimeError("`feature_extractors` and `config_path` cannot be specified at the same time")

        data_config = DetectionDataConfig(
            use_cache=use_cache,
            images_extractor=images_extractor,
            labels_extractor=labels_extractor,
            is_label_first=is_label_first,
            xyxy_converter=bbox_format,
        )

        # Check values of `n_classes` and `class_names` to define `class_names`.
        if n_classes and class_names:
            raise RuntimeError("`class_names` and `n_classes` cannot be specified at the same time")
        elif n_classes is None and class_names is None:
            raise RuntimeError("Either `class_names` or `n_classes` must be specified")
        class_names = class_names if class_names else list(map(str, range(n_classes)))

        # Define `class_names_to_use`
        if class_names_to_use:
            invalid_class_names_to_use = set(class_names_to_use) - set(class_names)
            if invalid_class_names_to_use != set():
                raise RuntimeError(f"You defined `class_names_to_use` with classes that are not listed in `class_names`: {invalid_class_names_to_use}")
        class_names_to_use = class_names_to_use or class_names

        grouped_feature_extractors = get_grouped_feature_extractors(
            default_config_name="detection",
            config_path=config_path,
            feature_extractors=feature_extractors,
        )

        batch_processor = DetectionBatchProcessor(
            data_config=data_config,
            n_image_channels=n_image_channels,
            class_names=class_names,
            class_names_to_use=class_names_to_use,
        )

        super().__init__(
            data_config=data_config,
            report_title=report_title,
            report_subtitle=report_subtitle,
            train_data=train_data,
            val_data=val_data,
            batch_processor=batch_processor,
            grouped_feature_extractors=grouped_feature_extractors,
            log_dir=log_dir,
            batches_early_stop=batches_early_stop,
            remove_plots_after_report=remove_plots_after_report,
        )
