from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import datetime
import google.generativeai as genai
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import io
import base64

# Load FD dataset
df = pd.read_csv("fd_rates_20_years.csv")
df["Date"] = pd.to_datetime(df["Date"])
fd_rate_col = "FD Rate (%)" if "FD Rate (%)" in df.columns else df.columns[-1]

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Gemini AI API Key
genai.configure(api_key="AIzaSyCFew-OOxPjDWG-6Sr93L5FyBLcfXfghao")

# Define request model
class FDRequest(BaseModel):
    tenure: str
    situation: str
    budget: float
    invest_year: int
    invest_month: int

# Get best FD recommendation
def get_best_fd(invest_year, invest_month):
    future_data = df[(df["Date"].dt.year == invest_year) & (df["Date"].dt.month == invest_month)]
    if future_data.empty:
        best_fd = df.loc[df[fd_rate_col].idxmax()]
    else:
        best_fd = future_data.loc[future_data[fd_rate_col].idxmax()]
    return best_fd["Bank"], best_fd[fd_rate_col], best_fd["Date"].year, best_fd["Date"].month

# Predict future FD rates
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

# Generate FD recommendation using Gemini AI
@app.post("/api/recommend")
async def generate_recommendation(request: FDRequest):
    best_bank, best_rate, year, month = get_best_fd(request.invest_year, request.invest_month)
    future_bank, future_rate, future_year, future_month = predict_future_best_fd(request.invest_year, request.invest_month)

    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"""A senior citizen is looking for the best FD investment recommendation:
    - Tenure: {request.tenure}
    - Financial situation: {request.situation}
    - Investment amount: {request.budget}
    - Planned Investment Date: {request.invest_month}/{request.invest_year}
    - Best Bank: {best_bank}
    - Best FD Rate: {best_rate:.2f}% (as of {month}/{year})
    - Future Best Bank (Prediction): {future_bank}
    - Future Best FD Rate: {future_rate:.2f}% (expected in {future_month}/{future_year})
    
    Provide a user-friendly recommendation.
    """

    response = model.generate_content(prompt)
    return {
        "recommendation": response.text,
        "best_bank": best_bank,
        "best_rate": best_rate,
        "year": year,
        "month": month
    }

# Generate FD growth projection
@app.post("/api/fd_plan")
async def generate_fd_plan(request: FDRequest):
    tenure_years = {"Short-term": 1, "Medium-term": 3, "Long-term": 5}
    years = tenure_years.get(request.tenure, 1)
    final_amount = request.budget * ((1 + request.budget / 100) ** years)

    return {
        "message": f"If you invest ₹{request.budget} at {request.budget:.2f}% for {years} years, you will get approximately ₹{final_amount:.2f} at maturity."
    }

# Generate FD trend graph
@app.get("/api/trend/{invest_month}/{invest_year}")
async def plot_fd_trend(invest_month: int, invest_year: int):
    month_data = df[(df["Date"].dt.month == invest_month) & (df["Date"].dt.year <= invest_year)]

    if month_data.empty:
        return JSONResponse(content={"error": "No historical data available."}, status_code=404)

    plt.figure(figsize=(10, 5))
    banks = month_data["Bank"].unique()
    for bank in banks:
        bank_data = month_data[month_data["Bank"] == bank]
        plt.plot(bank_data["Date"].dt.year, bank_data[fd_rate_col], marker='o', linestyle='-', label=bank)
    plt.xlabel("Year")
    plt.ylabel("FD Rate (%)")
    plt.title(f"FD Rate Trend ({invest_month}/{invest_year})")
    plt.legend()
    plt.grid()

    # Save image to buffer
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img_buf.getvalue()).decode("utf-8")
    return {"image": f"data:image/png;base64,{img_base64}"}
