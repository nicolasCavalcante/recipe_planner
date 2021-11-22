import json
from datetime import datetime, timedelta
from itertools import permutations, product
from pathlib import Path

import numpy as np
import pandas as pd
from tabulate import tabulate

SELF_PATH = Path(__file__).parent
DATA_PATH = SELF_PATH.parent / "data"
DATA_DEMO_PATH = SELF_PATH.parent / "data_demo"
DB_PATH = SELF_PATH.parent / "db"
MEALS_DB_PATH = DB_PATH / "meals_rep.json"
MEALPLANS_PATH = DB_PATH / "meal_plans"
SEMINFOPRATO = "sem registro de prato"


class PlannerDB:
    def __init__(
        self, receitaspath: Path = DATA_PATH / "Receitas.xlsx"
    ) -> None:
        self.mealsdb = MealsDB()
        self.receitas = pd.read_excel(receitaspath)

    def change_menu(self, date: datetime = datetime.now()):
        menudb = MenuDB(date)
        if menudb.load():
            self.mealsdb.increment_meals(menudb.db.Prato, -1)
        meals = self.mealsdb.pick_week_meals(self.receitas)
        menudb.update(meals)
        menudb.save()
        self.mealsdb.save()
        return menudb


class MealsDB:
    def __init__(self) -> None:
        self.db: dict = None
        self.__load_db()

    def pick_week_meals(self, df: pd.DataFrame):
        self.__load_db()
        self.__add_meals(df.Prato)
        meals = self.__pick_week_meals(df)
        meals = MealsDB.__spread_meals(meals)
        self.increment_meals(meals.Prato)
        return meals

    def increment_meals(self, pratos: pd.Series, amount: int = 1):
        for prato in pratos:
            if prato in self.db:
                self.db[prato] += amount

    def reset(self):
        for k in self.db:
            self.db[k] = 0

    def __load_db(self):
        if self.db is not None:
            return
        if not MEALS_DB_PATH.exists():
            self.db = {}
        else:
            with open(MEALS_DB_PATH) as f:
                self.db = json.load(f)

    def __add_meals(self, pratos: pd.Series):
        for prato in set(pratos):
            if prato not in self.db:
                self.db[prato] = 0

    def __pick_week_meals(self, df: pd.DataFrame):
        df = df.sample(frac=1)
        df["Repeticoes"] = [self.db[prato] for prato in df.Prato]
        meal_week = (
            df.loc[df["Dia da Semana"] != "Sab/Dom"]
            .sort_values(by=["Repeticoes"])
            .iloc[:5]
        )
        df.loc[
            [p in set(meal_week.Prato) for p in df.Prato], "Repeticoes"
        ] += 1
        meal_weekend = (
            df.loc[df["Dia da Semana"] != "Seg/Sex"]
            .sort_values(by=["Repeticoes"])
            .iloc[:2]
        )
        meals = pd.concat([meal_week, meal_weekend]).reset_index(drop=True)
        return meals

    @staticmethod
    def __spread_meals(meals: pd.DataFrame):
        order = meals.Carne.replace(
            dict((v, i) for i, v in enumerate(meals.Carne.unique()))
        ).values

        def score(order):
            vec_week = np.arange(order.size)
            scr = 0
            for i, v in enumerate(order):
                scrr = vec_week[order == v] - i
                scrr = scrr[scrr != 0]
                scr += np.abs(scrr).min() if len(scrr) else 0
            return scr

        perms = np.array(
            [
                a + b
                for a, b in product(
                    permutations(range(5)), permutations(range(5, 7))
                )
            ]
        )
        scores = [score(ord) for ord in order[perms]]
        return meals.iloc[perms[np.argmax(scores)]]

    def save(self):
        with open(MEALS_DB_PATH, "w") as f:
            json.dump(self.db, f, indent=4)


class MenuDB:
    def __init__(self, date: datetime) -> None:
        date = date - timedelta(date.weekday())
        meals_plan_name = date.strftime("%Y-%m-%d")
        self.path = MEALPLANS_PATH / f"{meals_plan_name}.cvs"
        self.db: pd.DataFrame = None

    def load(self):
        if self.path.exists():
            self.db = pd.read_csv(self.path, index_col=0)
            return True
        return False

    def update(
        self,
        meals: pd.DataFrame = pd.DataFrame(
            dict(Prato=[SEMINFOPRATO for _ in range(7)])
        ),
    ):
        df = pd.DataFrame(
            dict(
                Dia=[
                    "Segunda",
                    "Terca",
                    "Quarta",
                    "Quinta",
                    "Sexta",
                    "Sabado",
                    "Domingo",
                ],
                Prato=meals.Prato,
            )
        )
        # df = pd.DataFrame({
        #         "Dia": ["Segunda","Terca","Quarta","Quinta","Sexta","Sabado",
        #                 "Domingo"],
        #         "Café da Manhã": [None for _ in meals.Prato],
        #         "Almoço": meals.Prato,
        #         "Jantar": [None for _ in meals.Prato],
        #     })
        self.db = df.set_index("Dia")

    def save(self):
        self.db.to_csv(self.path)

    def __str__(self):
        return tabulate(self.db, tablefmt="pretty", headers="keys")


def main():
    db = PlannerDB(DATA_DEMO_PATH / "Receitas.xlsx")
    menudb = db.change_menu()
    print(menudb)


if __name__ == "__main__":
    main()
