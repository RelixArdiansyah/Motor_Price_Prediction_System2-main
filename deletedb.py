import pandas as pd

# Read the CSV file
df = pd.read_csv('olx.csv')

# Remove rows where company is 'Piaggio'
df = df[df['company'] != 'Piaggio']

# Save the modified dataframe back to CSV
df.to_csv('olx.csv', index=False)

print("All Piaggio entries have been removed from the dataset.")
