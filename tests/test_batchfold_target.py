import pytest
from batchfold.batchfold_target import BatchFoldTarget
from botocore.exceptions import ClientError
from Bio import SeqIO
import os

@pytest.fixture
def fold_target():
    target_id = "Test"
    bucket = "aws-af-testing"
    target = BatchFoldTarget(target_id=target_id, s3_bucket=bucket)
    assert target.target_id == target_id
    assert target.s3_bucket == bucket
    return target

def test_target_init():
    with pytest.raises(ClientError):
        BatchFoldTarget(target_id="Bad", s3_bucket="bd7907b46685f")

def test_validate_sequence(fold_target):
    assert BatchFoldTarget.validate_sequence("HEQAAKHHHAAAEHHEKG") is True
    with pytest.raises(ValueError):
        BatchFoldTarget.validate_sequence("1234?")

def test_add_sequence(fold_target):
    fold_target.add_sequence(
        seq_id="T1084",
        seq="MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH",
        description="Meio, Meiothermus silvanus, 73 residues|",
    ).upload_fasta()

    assert fold_target.sequences[0].id == "T1084"
    assert (
        fold_target.sequences[0].seq
        == "MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH"
    )
    assert (
        fold_target.sequences[0].description
        == "Meio, Meiothermus silvanus, 73 residues|"
    )
    assert fold_target.get_fasta_s3_uri() == "s3://aws-af-testing/Test/fastas/Test.fasta"
    file = fold_target.download_fasta("Test.fasta")
    with open(file) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            assert record.id == "T1084"
            assert (
                record.seq
                == "MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH"
            )
            assert (
                record.description == "T1084 Meio, Meiothermus silvanus, 73 residues|"
            )
    os.remove(file)