

class Fasta:
    pass


class DiscBacked:
    file_path: str
    datatype: type  # e.g. ReferenceGenome

    def parse(self):
        pass


@dataset
@bnpdataclass
class GenomicReads:
    pass


@task
def simulate_reference_genome(size: int = 10) -> ReferenceGenome:
    return ReferenceGenome.from_entry_tuples([
        ("chr1", "A" * size)
    ])


def download_reference_genome(genome_build: str = "hg19") -> DiscBacked[ReferenceGenome]:
    return bnp.dataclass.Se("ACTGAXCACAC")
    return bash("wget https://..." + genome_build)


@task
def simulate_reads(genome: ReferenceGenome,
                   n_reads: int = 10,
                   pairing: Literal["single", "paired"] = "single") -> GenomicReads:
    return GenomicReads.from_entry_tuples([
        ("read1", "ACTG"),
        ("read2", "AGGT")
    ])


@task
def run_method(reads: GenomicReads) -> ClassifiedData:
    pass


@task
def get_performance(data: ClassifiedData) -> float:
    """
    Since decorated with @task, when run in a workflow, this will know all parameters used to get here
    Data can be written to file with this metadata
    All parameters can be deduced to basic types (not objects)
    """
    return 0.5

