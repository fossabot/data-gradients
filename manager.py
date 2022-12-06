import concurrent
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Iterator

import yaml
import tqdm
from matplotlib import pyplot as plt

from data_validator.validator_abstract import ValidatorAbstract
from feature_extractors import FEATURE_EXTRACTORS, FeatureExtractorAbstract
from preprocess.preprocessor_abstract import PreprocessorAbstract
from logger.tensorboard_logger import TensorBoardLogger
from utils.data_classes import BatchData


debug_mode = True


class AnalysisManager:
    def __init__(self, args, train_data_iterator: Iterator, val_data_iterator: Optional[Iterator] = None):
        self._train_extractors: List[FeatureExtractorAbstract] = []
        self._val_extractors:   List[FeatureExtractorAbstract] = []
        self._threads = ThreadPoolExecutor()

        # Users Data Iterators
        self._train_only: bool = val_data_iterator is None
        self._train_iter: Iterator = train_data_iterator
        self._val_iter: Iterator = val_data_iterator

        # Logger
        self._logger = TensorBoardLogger()

        # Task Data Validator
        self._validator: ValidatorAbstract = ValidatorAbstract.get_validator(args.task)

        # Task Data Preprocessor
        self._preprocessor: PreprocessorAbstract = PreprocessorAbstract.get_preprocessor(args.task)

    def _get_feature_extractors(self, task: str) -> List:
        with open(self._yaml_path, "r") as stream:
            try:
                for key, value in yaml.safe_load(stream).items():
                    if key == task:
                        return value
            except yaml.YAMLError as exc:
                raise exc
        raise ValueError(f"Did not find right task, arg is {task} and couldn't find it in yaml")

    def build(self):
        # TODO: Might fold into hydra |  red  down there train_set
        fe_list = self._get_feature_extractors(self._task) + self._get_feature_extractors('general')
        for fe in fe_list:
            if isinstance(fe, str):
                self._train_extractors += [FEATURE_EXTRACTORS[fe](train_set=True)]
                self._val_extractors += [FEATURE_EXTRACTORS[fe](train_set=False)]
            elif isinstance(fe, dict):
                fe, params = next(iter(fe.items()))
                self._train_extractors += [FEATURE_EXTRACTORS[fe](True, **params)]
                self._val_extractors += [FEATURE_EXTRACTORS[fe](False, **params)]
            else:
                raise ValueError

    def validate_data_iterables(self):
        self._validator.validate(self._train_iter)
        if not self._train_only:
            self._validator.validate(self._val_iter)

    def _get_batch(self, dataloader) -> BatchData:
        images, labels = next(dataloader)
        bd = self._preprocessor.preprocess(images, labels)
        return bd

    def execute(self):
        # TODO: Maybe I do not need length?
        for train_batch in tqdm.trange(self._length_data):
            if train_batch > 3 and debug_mode:
                continue

            batch_data = self._get_batch(self._train_iter)

            for extractor in self._train_extractors:
                if not debug_mode:
                    futures = [self._threads.submit(extractor.execute, batch_data) for extractor in
                               self._train_extractors]
                else:
                    extractor.execute(batch_data)

            if not self._train_only:
                try:
                    batch_data = self._get_batch(self._val_iter)
                except StopIteration:
                    self._train_only = True
                else:
                    for extractor in self._val_extractors:
                        if not debug_mode:
                            futures += [self._threads.submit(extractor.execute, batch_data) for extractor in
                                        self._val_extractors]
                        else:
                            extractor.execute(batch_data)

            if not debug_mode:
                # Wait for all threads to finish
                concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)

    def post_process(self):
        for val_extractor, train_extractor in zip(self._val_extractors, self._train_extractors):
            fig, ax = plt.subplots()

            # First val - because graph params will be overwritten by latest (train) and we want it's params
            if not self._train_only:
                val_extractor.process(ax)

            train_extractor.process(ax)

            fig.tight_layout()

            self._logger.log_graph(val_extractor.__class__.__name__ + "/fig", fig)

    def close(self):
        self._logger.close()

    def run(self):
        self.build()
        self.validate_data_iterables()
        self.execute()
        self.post_process()
        self.close()
