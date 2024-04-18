import pandas as pd
import json

with open("hello_kitty.json", "r") as file:
    data = json.load(file)

dataframes = {
    "depop": pd.DataFrame(data["depop"]),
    "grailed": pd.DataFrame(data["grailed"]),
}

for key, value in dataframes.items():
    print(f"{key}: {value}.to_string()")
