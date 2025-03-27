import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import datetime
import google.generativeai as genai

# Load FD dataset
df = pd.read_csv("fd_rates_20_years.csv")
df["Date"] = pd.to_datetime(df["Date"])

# Ensure column name matches actual dataset
print("Dataset Columns:", df.columns)
fd_rate_col = "FD Rate (%)" if "FD Rate (%)" in df.columns else df.columns[-1]

# Get today's month and year for default values
today = datetime.date.today()
default_month = today.month
default_year = today.year

def get_best_fd(tenure, situation, budget, invest_year, invest_month):
    future_data = df[(df["Date"].dt.year == invest_year) & (df["Date"].dt.month == invest_month)]
    if future_data.empty:
        best_fd = df.loc[df[fd_rate_col].idxmax()]
    else:
        best_fd = future_data.loc[future_data[fd_rate_col].idxmax()]
    return best_fd["Bank"], best_fd[fd_rate_col], best_fd["Date"].year, best_fd["Date"].month

def predict_future_best_fd(invest_year, invest_month):
    month_data = df[df["Date"].dt.month == invest_month]
    
    if month_data.empty:
        return "No data", 0.0, invest_year + 1, invest_month  

    X = month_data["Date"].dt.year.values.reshape(-1, 1)
    y = month_data[fd_rate_col].values  

    model = LinearRegression()
    model.fit(X, y)

    future_year = invest_year + 1
    future_rate = model.predict(np.array([[future_year]]))[0]

    best_fd = month_data.loc[month_data[fd_rate_col].idxmax()]

    return best_fd["Bank"], round(future_rate, 2), future_year, invest_month

def generate_recommendation(tenure, situation, budget, invest_year, invest_month):
    genai.configure(api_key="AIzaSyCFew-OOxPjDWG-6Sr93L5FyBLcfXfghao")
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    best_bank, best_rate, year, month = get_best_fd(tenure, situation, budget, invest_year, invest_month)
    future_bank, future_rate, future_year, future_month = predict_future_best_fd(invest_year, invest_month)
    
    prompt = f"""A senior citizen is looking for the best FD investment recommendation:
    - Tenure: {tenure}
    - Financial situation: {situation}
    - Investment amount: {budget}
    - Planned Investment Date: {invest_month}/{invest_year}
    - Best Bank: {best_bank}
    - Best FD Rate: {best_rate:.2f}% (as of {month}/{year})
    - Future Best Bank (Prediction): {future_bank}
    - Future Best FD Rate: {future_rate:.2f}% (expected in {future_month}/{future_year})
    
    Provide a user-friendly recommendation that includes:
    1. **Best FD Plan**
    2. **Best Bank** with highest FD rates
    3. **Expected Interest Rate**
    4. **Benefits** (e.g., extra interest for seniors)
    5. **Potential Risks** (mention risks clearly).
    6. **Optimal Future Investment Month and Year** based on trend analysis.
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_fd_plan(budget, best_rate, tenure):
    tenure_years = {"Short-term": 1, "Medium-term": 3, "Long-term": 5}
    years = tenure_years.get(tenure, 1)
    final_amount = budget * ((1 + best_rate / 100) ** years)
    return f"If you invest ₹{budget} at {best_rate:.2f}% for {years} years, you will get approximately ₹{final_amount:.2f} at maturity."

def plot_fd_trend(invest_month, invest_year):
    month_data = df[(df["Date"].dt.month == invest_month) & (df["Date"].dt.year <= invest_year)]

    if month_data.empty:
        print("No historical data available for this month.")
        return

    banks = month_data["Bank"].unique()

    for bank in banks:
        bank_data = month_data[month_data["Bank"] == bank]
        
        plt.figure(figsize=(10, 5))
        plt.plot(bank_data["Date"].dt.year, bank_data[fd_rate_col], marker='o', linestyle='-', label=bank)
        plt.xlabel("Year")
        plt.ylabel("FD Rate (%)")
        plt.title(f"FD Rate Trend for {bank} (Month {invest_month})")
        plt.legend()
        plt.grid()
        plt.show()

def main():
    print("Welcome to the Senior Citizen FD Advisor!")
    print("Please answer the following questions to get the best FD plan recommendations.")
    
    tenure = input("What tenure are you looking for? (Short-term, Medium-term, Long-term): ")
    situation = input("What is your current financial situation? (Need liquidity, Secure savings, Growth focus): ")
    budget = float(input("What is your investment amount? (e.g., 10000, 50000, 100000): "))
    
    # Default values based on the current date
    print(f"Default Investment Year: {default_year}")
    print(f"Default Investment Month: {default_month}")
    
    invest_year = input(f"Enter the year you plan to invest [{default_year}]: ")
    invest_year = int(invest_year) if invest_year else default_year  # Use input or default value

    invest_month = input(f"Enter the month you plan to invest (1-12) [{default_month}]: ")
    invest_month = int(invest_month) if invest_month else default_month  # Use input or default value
    
    recommendation = generate_recommendation(tenure, situation, budget, invest_year, invest_month)
    best_bank, best_rate, _, _ = get_best_fd(tenure, situation, budget, invest_year, invest_month)
    fd_plan = generate_fd_plan(budget, best_rate, tenure)
    
    print("\n✨ Personalized FD Recommendation ✨")
    print(recommendation)
    print("\n💰 FD Growth Projection 💰")
    print(fd_plan)
    
    # Plot FD trend for each bank
    print("\n📈 Generating FD Rate Trend Graphs...")
    plot_fd_trend(invest_month, invest_year)

if __name__ == "__main__":
    main()
