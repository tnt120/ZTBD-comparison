import sys
import os
from .import_postgres import load_postgres
from .import_mysql import load_mysql
from .import_mongo import import_mongo


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from common.utils import print_colored


def import_parameters():
    print_colored("Postgres", "BLUE")
    try:
        units_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "source/units.sql"
        )
        parameters_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "source/parameters.sql"
        )

        load_postgres(units_file_path, "Units")
        load_postgres(parameters_file_path, "Parameters")
    except:
        print_colored("Failed loading postgres", "RED")

    print_colored("MySQL", "BLUE")
    try:
        units_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "source/units.sql"
        )
        parameters_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "source/parameters.sql"
        )

        load_mysql(units_file_path, "Units")
        load_mysql(parameters_file_path, "Parameters")
    except:
        print_colored("Failed loading mysql", "RED")

    units_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/units.json"
    )
    parameters_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/parameters.json"
    )

    print_colored("Mongo 6", "BLUE")
    try:
        import_mongo(
            MONGO6_HOST,
            MONGO6_PORT,
            MONGO6_USER,
            MONGO6_PASSWORD,
            MONGO6_DB,
            units_file_path,
            "units",
        )

        print_colored(f"[Mongo 6] Units loaded successfully.", "GREEN")

        import_mongo(
            MONGO6_HOST,
            MONGO6_PORT,
            MONGO6_USER,
            MONGO6_PASSWORD,
            MONGO6_DB,
            parameters_file_path,
            "parameters",
        )

        print_colored(f"[Mongo 6] Units loaded successfully.", "GREEN")
    except:
        print_colored("Failed loading mongo 6", "RED")

    print_colored("Mongo 8", "BLUE")
    try:
        import_mongo(
            MONGO8_HOST,
            MONGO8_PORT,
            MONGO8_USER,
            MONGO8_PASSWORD,
            MONGO8_DB,
            units_file_path,
            "units",
        )

        print_colored(f"[Mongo 8] Units loaded successfully.", "GREEN")

        import_mongo(
            MONGO8_HOST,
            MONGO8_PORT,
            MONGO8_USER,
            MONGO8_PASSWORD,
            MONGO8_DB,
            parameters_file_path,
            "parameters",
        )

        print_colored(f"[Mongo 8] Units loaded successfully.", "GREEN")
    except:
        print_colored("Failed loading mongo 8", "RED")


if __name__ == "__main__":
    import_parameters()
