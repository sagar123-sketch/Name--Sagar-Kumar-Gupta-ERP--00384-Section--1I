import os
import pandas as pd
import matplotlib.pyplot as plt

def create_default_csv(filename="population.csv"):
    if not os.path.exists(filename):
        data = """City,Year,Population
Raipur,2020,1000000
Raipur,2024,1100000
Durg,2020,500000
Durg,2024,600000"""
        with open(filename, "w") as f:
            f.write(data)

def load_and_clean_data(filename="population.csv"):
    create_default_csv(filename)
    try:
        raw_df = pd.read_csv(filename, dtype=str)
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()

    if list(raw_df.columns) != ["City", "Year", "Population"]:
        raw_df = pd.read_csv(filename, names=["City", "Year", "Population"], dtype=str)

    valid_rows = []
    skipped = False

    for idx, row in raw_df.iterrows():
        row_num = idx + 1
        city = str(row["City"]).strip()
        year_str = str(row["Year"]).strip()
        pop_str = str(row["Population"]).strip()

        try:
            year = int(year_str)
        except ValueError:
            print(f"Row {row_num} skipped: invalid Year '{year_str}'")
            skipped = True
            continue

        try:
            pop = int(float(pop_str))
        except ValueError:
            print(f"Row {row_num} skipped: invalid Population '{pop_str}'")
            skipped = True
            continue

        if pop <= 0:
            print(f"Row {row_num} skipped: Population must be positive")
            skipped = True
            continue

        valid_rows.append({"City": city, "Year": year, "Population": pop})

    if skipped:
        print(f"Valid rows: {len(valid_rows)}")

    df = pd.DataFrame(valid_rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["City", "Year"], keep="last")
    return df

def calculate_metrics(df):
    df_sorted = df.sort_values(by=["City", "Year"])
    grouped = df_sorted.groupby("City", sort=False)

    latest_records = grouped.last().reset_index()
    earliest_records = grouped.first().reset_index()

    merged = pd.merge(earliest_records, latest_records, on="City", suffixes=("_earliest", "_latest"))
    
    growth_data = {}
    has_multi_year = False

    for _, row in merged.iterrows():
        city = row["City"]
        if row["Year_latest"] > row["Year_earliest"]:
            has_multi_year = True
            earliest_pop = row["Population_earliest"]
            latest_pop = row["Population_latest"]
            growth = ((latest_pop - earliest_pop) / earliest_pop) * 100
            growth_data[city] = growth

    return latest_records, growth_data, has_multi_year

def show_summary(df):
    if df.empty:
        print("No valid data available.")
        return

    latest_records, growth_data, has_multi_year = calculate_metrics(df)
    
    max_year = df["Year"].max()
    latest_year_df = df[df["Year"] == max_year]
    total_pop = latest_year_df["Population"].sum()
    
    largest_row = latest_year_df.loc[latest_year_df["Population"].idxmax()]
    largest_city = largest_row["City"]
    largest_pop = largest_row["Population"]

    if len(df) == 1 or not has_multi_year:
        print(f"Total population: {total_pop} | Largest city: {largest_city}")
        print("Growth: not available (only one year of data)")
    else:
        print(f"Total population ({max_year}): {total_pop}")
        print(f"Largest city: {largest_city} ({largest_pop})")
        fastest_city = max(growth_data, key=growth_data.get)
        fastest_val = growth_data[fastest_city]
        sign = "+" if fastest_val >= 0 else ""
        print(f"Fastest growing: {fastest_city} ({sign}{fastest_val:.2f}%)")

def show_growth_and_charts(df):
    if df.empty:
        print("No valid data available.")
        return

    _, growth_data, has_multi_year = calculate_metrics(df)

    if not has_multi_year:
        print("Growth: not available (only one year of data)")
        return

    growth_Parts = []
    for city, val in growth_data.items():
        sign = "+" if val >= 0 else ""
        growth_Parts.append(f"{city}: {sign}{val:.2f}%")
    print(" | ".join(growth_Parts))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    cities = list(growth_data.keys())
    growths = list(growth_data.values())
    ax1.bar(cities, growths, color="skyblue", edgecolor="black")
    ax1.set_title("Population Growth by City")
    ax1.set_xlabel("City")
    ax1.set_ylabel("Growth (%)")

    for city, group in df.sort_values("Year").groupby("City"):
        ax2.plot(group["Year"].astype(str), group["Population"], marker="o", label=city)
    
    ax2.set_title("Population Trend")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Population")
    ax2.legend()

    plt.tight_layout()
    print("Bar chart 'Population Growth by City' and line chart 'Population Trend' displayed")
    plt.show()

def main():
    filename = "population.csv"
    df = load_and_clean_data(filename)
    
    if df.empty:
        return

    print("\n1. Summary")
    print("2. Growth and charts")
    choice = input("Select menu option (1 or 2): ").strip()

    if choice == "1":
        show_summary(df)
    elif choice == "2":
        show_growth_and_charts(df)
    else:
        print("Invalid menu option.")

if __name__ == "__main__":
    main()