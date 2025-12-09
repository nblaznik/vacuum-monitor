import pandas as pd

def fix_csv(input_file, output_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Replace pressure values for Channel 1 with 1.000E-11

    df.loc[df['Channel'] == 1, 'Pressure'] = '1.000E-11'

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"File has been updated and saved as {output_file}")

# Example usage:
input_file = 'pressure_readings.csv'  # Replace with your input CSV file
output_file = 'pressure_readings.csv'  # Replace with the desired output CSV file
fix_csv(input_file, output_file)
