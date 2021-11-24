import json
from datetime import timedelta
from pathlib import Path

import requests
import typer

import recipe_planner.planner as planner


def main(
    meals_spreadsheet_name: str = "Receitas",
    weeks_in_future: int = 0,
    demo: bool = False,
    update: bool = True,
):
    configpath = Path(__file__).parent.parent / "config/api_config.json"
    with open(configpath, "r") as f:
        cfg = json.load(f)
    menudb, date, updated = planner.main(
        meals_spreadsheet_name,
        weeks_in_future + 1,
        demo,
        update,
    )
    if not updated:
        return
    from_date, to_date = date, date + timedelta(7)
    text = (
        f"Calendário da semana do dia {from_date.strftime('%d/%m/%Y')}"
        f" ao dia {to_date.strftime('%d/%m/%Y')}\n{menudb}"
    )
    print(text)
    requests.post(
        f"{cfg['url']}?phone={cfg['phone']}"
        f"&text={text}&apikey={cfg['apikey']}",
    )


def app():
    typer.run(main)


if __name__ == "__main__":
    main(demo=True)
