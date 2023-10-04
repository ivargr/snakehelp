import bionumpy as bnp
from typing import Literal

class Fasta:
    pass


class DiscBacked:
    file_path: str
    datatype: type  # e.g. ReferenceGenome

    def parse(self):
        pass



class SimulatedHeatmap(Heatmap):
    pass


def simulate_heatmap(n: int, m: int) -> SimulatedHeatmap:
    pass


def get_heatmap_from_reads(reads: GenomicReads) -> RealHeatmap:
    pass


#@dataset
#@bnpdataclass
class GenomicReads:
    pass



#@bnp.dataclass
class ReferenceGenome:
    pass

#@task
def simulate_reference_genome(size: int = 10) -> ReferenceGenome:
    return "".join([random.choice(["A", "C", "T", "G"]) for i in range(10)]) # "AAAAAAAAAACACAC"
    return ReferenceGenome.from_entry_tuples([
        ("chr1", "A" * size)
    ])



#@task
def simulate_reads(genome: ReferenceGenome,
                   n_reads: int = 10,
                   pairing: Literal["single", "paired"] = "single") -> GenomicReads:
    return "AAA"
    return GenomicReads.from_entry_tuples([
        ("read1", "ACTG"),
        ("read2", "AGGT")
    ])


#@task
def run_method(reads: GenomicReads):
    return []
    for read in reads:
        if "A" in read:
            yield 1
    pass


#@task
def get_performance(data) -> float:
    """
    Since decorated with @task, when run in a workflow, this will know all parameters used to get here
    Data can be written to file with this metadata
    All parameters can be deduced to basic types (not objects)
    """
    return 0.0



performance = get_performance(run_method(simulate_reads(simulate_reference_genome(), n_reads=1000)))
assert performance >= 0.0

performane_random_data = ....
assert performance == 0.5



#task SImulateGenomicReads > DownloadGenomicReads

