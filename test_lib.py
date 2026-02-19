import pandas as pd
import matplotlib.pyplot as plt

data = {
    "name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack", "Karen"],
    "age": [30, 40, 25, 35, 28, 32, 45, 38, 29, 31, 33],
    "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin"]
}
df = pd.DataFrame(data)

df.hist()
plt.savefig('output.png')  # Save the plot to a file instead of showing it

print(df.describe())


