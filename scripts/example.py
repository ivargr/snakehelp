from snakehelp.snakehelp import Parameters
from dataclasses import dataclass
from typing import Literal


@dataclass
class ReferenceGenome(Parameters):
    genome_build: str
    random_seed: int
    dataset_size: Literal["small", "medium", "big"]


@dataclass
class SimulatedReads(Parameters):
    reference_genome: ReferenceGenome
    error_rate: float
    n_reads: int

