from typing import Callable, Union, Tuple, List, Mapping

import PIL
import numpy as np
import torch

from data_gradients.batch_processors.adapters.tensor_extractor import get_tensor_extractor_options
from data_gradients.batch_processors.adapters.utils import to_torch
from data_gradients.config.data.data_config import DataConfig
from data_gradients.config.data.questions import Question, text_to_yellow
from data_gradients.batch_processors.adapters.common_extractors.base import BaseDatasetExtractor, AutoExtractor

SupportedData = Union[Tuple, List, Mapping, Tuple, List]


class ImageExtractorError(Exception):
    def __init__(self):
        msg = (
            "\n\nERROR: Something went wrong when extracting Images!\n\n"
            "Please implement and pass to the config the following function\n"
            "`images_extractor(data: Any) -> torch.Tensor`\n\n"
            "- `data` being the output of the dataset/dataloader that you provided.\n"
            "- The function should return a Tensor representing your image(s). One of:\n"
            "  - `(BS, C, H, W)`, `(BS, H, W, C)`, `(BS, H, W)` for batch\n"
            "  - `(C, H, W)`, `(H, W, C)`, `(H, W)` for single image\n"
            "    - With `C`: number of channels (3 for RGB)\n\n"
            "You can find more information about `images_extractor` in the documentation: https://github.com/Deci-AI/data-gradients\n"
        )
        super().__init__(msg)


class LabelsExtractorError(Exception):
    def __init__(self):
        msg = (
            "\n\nERROR: Something went wrong when extracting Labels!\n\n"
            "Please implement and pass to the config the following function:\n"
            "`labels_extractor(data: Any) -> torch.Tensor`\n\n"
            "- `data` being the output of the dataset/dataloader that you provided.\n"
            "- The function should return a Tensor representing your labels(s):\n"
            "  - For **Segmentation**, one of:\n"
            "    - `(BS, C, H, W)`, `(BS, H, W, C)`, `(BS, H, W)` for batch\n"
            "    - `(C, H, W)`, `(H, W, C)`, `(H, W)` for single image\n"
            "      - `BS`: Batch Size\n"
            "      - `C`: number of channels - 3 for RGB\n"
            "      - `H`, `W`: Height and Width\n"
            "  - For **Detection**, one of:\n"
            "    - `(BS, N, 5)`, `(N, 6)` for batch\n"
            "    - `(N, 5)` for single image\n"
            "      - `BS`: Batch Size\n"
            "      - `N`: Padding size\n"
            "      - The last dimension should include your `class_id` and `bbox` - `class_id, x, y, x, y` for instance\n\n"
            "You can find more information about `labels_extractors` in the documentation: https://github.com/Deci-AI/data-gradients\n"
        )
        super().__init__(msg)


class DatasetAdapter:
    """Class responsible to convert raw batch (coming from dataloader) into a batch of image and a batch of labels."""

    def __init__(self, data_config: DataConfig, predefined_extractors: List[BaseDatasetExtractor]):
        self.data_config = data_config
        self.auto_extractor = AutoExtractor(predefined_extractors)

    def extract(self, data: SupportedData) -> Tuple[torch.Tensor, torch.Tensor]:
        """Convert raw batch (coming from dataloader) into a batch of image and a batch of labels.

        :param data: Raw batch (coming from dataloader without any modification).
        :return:
            - images: Batch of images
            - labels: Batch of labels
        """
        images = self._extract_images(data)
        labels = self._extract_labels(data)
        return to_torch(images), to_torch(labels)

    def _extract_images(self, data: SupportedData) -> torch.Tensor:
        images_extractor = self._get_images_extractor(data)
        return images_extractor(data)

    def _extract_labels(self, data: SupportedData) -> torch.Tensor:
        labels_extractor = self._get_labels_extractor(data)
        return labels_extractor(data)

    def _get_images_extractor(self, data: SupportedData) -> Callable[[SupportedData], torch.Tensor]:
        if self.data_config.images_extractor is not None:
            return self.data_config.get_images_extractor()

        # We use the heuristic that a tuple of 2 should represent (image, label) in this order
        if isinstance(data, (Tuple, List)) and len(data) == 2:
            if isinstance(data[0], (torch.Tensor, np.ndarray, PIL.Image.Image)):
                self.data_config.images_extractor = "[0]"  # We save it for later use
                return self.data_config.get_images_extractor()  # This will return a callable

        if self.auto_extractor.find_extractor(data=data):
            dataset_extractor = self.auto_extractor.find_extractor(data=data)
            self.data_config.images_extractor = dataset_extractor.images_extractor(data)
            return self.data_config.get_images_extractor()  # This will return a callable

        # Otherwise, we ask the user how to map data -> image
        if isinstance(data, (Tuple, List, Mapping, Tuple, List)):
            description, options = get_tensor_extractor_options(data)
            question = Question(question=f"Which tensor represents your {text_to_yellow('Image(s)')} ?", options=options)
            return self.data_config.get_images_extractor(question=question, hint=description)

        raise NotImplementedError(
            f"Got object {type(data)} from Data Iterator which is not supported!\n"
            f"Please implement a custom `images_extractor` for your dataset. "
            f"You can find more detail about this in our documentation: https://github.com/Deci-AI/data-gradients"
        )

    def _get_labels_extractor(self, data: SupportedData) -> Callable[[SupportedData], torch.Tensor]:
        if self.data_config.labels_extractor is not None:
            return self.data_config.get_labels_extractor()

        # We use the heuristic that a tuple of 2 should represent (image, label) in this order
        if isinstance(data, (Tuple, List)) and len(data) == 2:
            if isinstance(data[1], (torch.Tensor, np.ndarray, PIL.Image.Image)):
                self.data_config.labels_extractor = "[1]"  # We save it for later use
                return self.data_config.get_labels_extractor()  # This will return a callable

        if self.auto_extractor.find_extractor(data=data):
            dataset_extractor = self.auto_extractor.find_extractor(data=data)
            self.data_config.labels_extractor = dataset_extractor.labels_extractor
            return self.data_config.get_labels_extractor()  # This will return a callable

        # Otherwise, we ask the user how to map data -> labels
        if isinstance(data, (Tuple, List, Mapping, Tuple, List)):
            description, options = get_tensor_extractor_options(data)
            question = Question(question=f"Which tensor represents your {text_to_yellow('Label(s)')} ?", options=options)
            return self.data_config.get_labels_extractor(question=question, hint=description)

        raise NotImplementedError(
            f"Got object {type(data)} from Data Iterator which is not supported!\n"
            f"Please implement a custom `labels_extractor` for your dataset. "
            f"You can find more detail about this in our documentation: https://github.com/Deci-AI/data-gradients"
        )
