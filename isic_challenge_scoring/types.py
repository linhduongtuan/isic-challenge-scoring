from dataclasses import dataclass
from typing import Dict, Union


class ScoreException(Exception):
    pass


SeriesDict = Dict[str, float]
DataFrameDict = Dict[str, SeriesDict]
ScoreDict = Dict[str, Union[float, SeriesDict, DataFrameDict, Dict[str, DataFrameDict]]]


@dataclass
class Score:
    overall: float
    validation: float

    def to_string(self) -> str:
        output = f'Overall: {self.overall}\n'
        output += f'Validation: {self.validation}'
        return output

    def to_dict(self) -> ScoreDict:
        return {'overall': self.overall, 'validation': self.validation}
