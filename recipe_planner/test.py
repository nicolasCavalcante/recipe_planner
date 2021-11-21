from pathlib import Path

import pandas as pd

SELF_PATH = Path(__file__).parent
MEALS_DB_PATH = SELF_PATH / "meals_rep.csv"


class ReceitaDB:
    def __init__(self) -> None:
        if not MEALS_DB_PATH.exists():
            MEALS_DB_PATH.touch()
            with open(MEALS_DB_PATH, "w") as f:
                f.write("Prato,Repeticoes")
        self.db = pd.read_csv(MEALS_DB_PATH)

    def add_meals(self, df: pd.DataFrame):
        pratos = set(self.db.Prato)
        for prato in set(df.Prato):
            if prato not in pratos:
                self.db = self.db.append(
                    dict(Prato=prato, Repeticoes=0), ignore_index=True
                )
        self.save()

    def pick_week_meal_plan(self, df: pd.DataFrame):
        df = df.sample(frac=1).merge(
            self.db, left_on="Prato", right_on="Prato"
        )
        df_cp = df.copy()
        meal_week = (
            df.loc[df["Dia da Semana"] != "Sab/Dom"]
            .sort_values(by=["Repeticoes"])
            .iloc[:5]
        )
        df.loc[
            [p in set(meal_week.Prato) for p in df.Prato], "Repeticoes"
        ] += 1
        meal_weekend = (
            df_cp.loc[df["Dia da Semana"] != "Seg/Sex"]
            .sort_values(by=["Repeticoes"])
            .iloc[:2]
        )
        return meal_week, meal_weekend

    def increment_meals(self, df: pd.DataFrame):
        self.db.loc[
            [p in set(df.Prato) for p in self.db.Prato], "Repeticoes"
        ] += 1
        self.save()

    def save(self):
        self.db.to_csv(MEALS_DB_PATH, index=False, header=True)


def main():
    db = ReceitaDB()
    df = pd.read_excel(SELF_PATH.parent / "data/Receitas.xlsx")
    db.add_meals(df)
    meal_week, meal_weekend = db.pick_week_meal_plan(df)
    db.increment_meals(meal_week)
    db.increment_meals(meal_weekend)


if __name__ == "__main__":
    main()
