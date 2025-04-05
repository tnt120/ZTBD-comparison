import sys
import os
import glob
import argparse

base_dir = os.path.dirname(os.path.abspath(__file__))

for folder in glob.glob(os.path.join(base_dir, "*/")):
    if os.path.isdir(folder):
        sys.path.append(os.path.abspath(folder))

from drop_schema.drop_schema import drop_schema
from apply_schema.apply_schema import apply_schema
from import_drugs.load_all import load_drugs
from import_users.import_users import import_users
from import_parameters.import_parameters import import_parameters
from generate_parameter_logs.generate import generate as generate_parameter_logs
from generate_parameter_logs.defaults import (
    DEFAULT_RECORDS_COUNT as DEFAULT_PARAMETER_LOGS_COUNT,
)
from generate_parameter_logs.import_all import import_all as import_parameter_logs
from generate_user_drugs.generate import generate as generate_user_drugs
from generate_user_drugs.defaults import (
    DEFAULT_RECORDS_COUNT as DEFAULT_USER_DRUGS_COUNT,
)
from generate_user_drugs.import_all import import_all as import_user_drugs
from generate_drug_logs.generate import generate as generate_drug_logs
from generate_drug_logs.defaults import DEFAULT_RECORDS_COUNT as DEFAULT_DRUG_LOGS_COUNT
from generate_drug_logs.import_all import import_all as import_drug_logs
from common.utils import print_colored


def _parse_args():
    parser = argparse.ArgumentParser(description="Parameter logs import script options")

    parser.add_argument(
        "--start-of",
        type=int,
        default=1,
        help="Which step to start of. By default from the beginning.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    start_step = _parse_args().start_of

    if start_step <= 1:
        print_colored("1. Dropping existing schema\n", "YELLOW")
        drop_schema()

    if start_step <= 2:
        print_colored("\n2. Applying schema\n", "YELLOW")
        apply_schema()

    if start_step <= 3:
        print_colored("\n3. Importing drugs\n", "YELLOW")
        load_drugs()

    if start_step <= 4:
        print_colored("\n4. Importing users\n", "YELLOW")
        import_users()

    if start_step <= 5:
        print_colored("\n5. Importing parameters\n", "YELLOW")
        import_parameters()

    if start_step <= 6:
        print_colored("\n6. Generate parameter logs", "YELLOW")
        raw_input = input(
            f"How many records to generate? [{DEFAULT_PARAMETER_LOGS_COUNT}]: "
        )
        rec_count = (
            int(raw_input) if raw_input.strip() else DEFAULT_PARAMETER_LOGS_COUNT
        )

        generate_parameter_logs(rec_count)

        raw_input = input(
            f"How many records to insert? [{DEFAULT_PARAMETER_LOGS_COUNT}]: "
        )
        rec_count = (
            int(raw_input) if raw_input.strip() else DEFAULT_PARAMETER_LOGS_COUNT
        )

        import_parameter_logs(rec_count)

    if start_step <= 7:
        print_colored("\n7. Generate user drugs", "YELLOW")
        generate_user_drugs()

        raw_input = input(f"How many records to insert? [{DEFAULT_USER_DRUGS_COUNT}]: ")
        rec_count = int(raw_input) if raw_input.strip() else DEFAULT_USER_DRUGS_COUNT

        import_user_drugs(rec_count)

    if start_step <= 8:
        print_colored("\n8. Generate drug logs", "YELLOW")

        raw_input = input(
            f"How many records to generate? [{DEFAULT_DRUG_LOGS_COUNT}]: "
        )
        rec_count = int(raw_input) if raw_input.strip() else DEFAULT_DRUG_LOGS_COUNT

        generate_drug_logs(rec_count)

        raw_input = input(f"How many records to insert? [{DEFAULT_DRUG_LOGS_COUNT}]: ")
        rec_count = int(raw_input) if raw_input.strip() else DEFAULT_DRUG_LOGS_COUNT

        import_drug_logs(rec_count)

    print_colored("\nSetup complete", "GREEN")
