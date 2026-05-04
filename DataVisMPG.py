import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#import the file such that we can pull from it
file_path = 'auto+mpg/auto-mpg.data'
#time to format
column_names = ['MPG', 'Cylinders', 'Displacement', 'Horsepower', 'Weight','Acceleration', 'Model Year', 'Origin']
#data frame
df = pd.read_csv(file_path, names = column_names, na_values='?', comment='\t', sep=" ", skipinitialspace=True)

#Visualization 1 Scatter plot (Weight vs MPG)
plt.figure(figsize=(8,5))
sns.scatterplot(x='Weight', y='MPG', data = df, color='blue', alpha=0.6)
plt.title('Impact of Vehicle Weight on Fuel Efficiency')
plt.xlabel('Weight (lbs)')
plt.ylabel('Miles per Gallon (MPG)')
plt.grid(True, linestyle='--', alpha=0.7)
#plt.savefig('weight_vs_mpg.png')
plt.show()

#Visualization 2 box plot cyls vs mpg
plt.figure(figsize=(8,5))
sns.boxplot(x='Cylinders', y='MPG', data = df, palette='Set2')
plt.title('MPG Distribution by Number of Cylinders')
plt.xlabel('Number of Cylinders')
plt.ylabel('Miles per Gallon (MPG)')
#plt.savefig('cylinders_vs_mpg.png')
plt.show()

print(df.head())