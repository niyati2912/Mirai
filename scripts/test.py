# import pandas as pd

# df = pd.read_csv("data/processed/master_dataset.csv")

# print(df.head())
# print(df.columns.tolist())
# print(df.shape)

# import pandas as pd

# df = pd.read_csv("data/processed/master_dataset.csv")

# print(df.columns)

# import pandas as pd

# df = pd.read_csv("data/processed/feature_table.csv")

# print(df.columns.tolist())

# print("ESS_target" in df.columns)

import pandas as pd

df = pd.read_csv("data/processed/feature_table.csv")

print(df["ESS"].head(20))
print()
print(df["ESS"].tail(20))