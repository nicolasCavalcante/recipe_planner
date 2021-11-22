from datetime import datetime

import typer

from recipe_planner.planner import DATA_DEMO_PATH, DATA_PATH, PlannerDB


def main(
    meals_spreadsheet_name: str = "Receitas",
    date: datetime = datetime.now(),
    demo: bool = False,
):
    path = DATA_DEMO_PATH if demo else DATA_PATH
    db = PlannerDB(path / f"{meals_spreadsheet_name}.xlsx")
    menudb = db.change_menu(date)
    print(menudb)


app = typer.run(main)
if __name__ == "__main__":
    main()
