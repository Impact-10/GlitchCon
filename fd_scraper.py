import requests
from bs4 import BeautifulSoup
import json

# Extract FD rates organized by tenure
def get_fd_rates_by_tenure(bank_name, url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        fd_content = (soup.find("table") or
                      soup.find("div", class_="rates") or
                      soup.find("section") or
                      soup.find("article") or
                      soup.find("div", class_="content") or
                      soup.find("ul"))

        if not fd_content:
            return {}

        rows = fd_content.find_all("tr") if fd_content.name == "table" else [fd_content]

        rates_by_tenure = {}

        for row in rows:
            cols = row.find_all("td") if row.name == "tr" else [row]
            if len(cols) >= 3:
                tenure = cols[0].text.strip()
                try:
                    senior_rate = float(cols[2].text.strip().replace("%", ""))
                    if tenure not in rates_by_tenure:
                        rates_by_tenure[tenure] = {}
                    rates_by_tenure[tenure][bank_name] = f"{senior_rate}%"
                except ValueError:
                    continue
        
        return rates_by_tenure
    else:
        return {}

# Bank URLs
banks = {
    "HDFC": "https://www.hdfcbank.com/personal/save/deposits/fixed-deposit-interest-rate",
}

# Combine data from all banks
final_rates_by_tenure = {}

for bank, url in banks.items():
    bank_rates = get_fd_rates_by_tenure(bank, url)
    for tenure, rate_info in bank_rates.items():
        if tenure not in final_rates_by_tenure:
            final_rates_by_tenure[tenure] = {}
        final_rates_by_tenure[tenure].update(rate_info)

# Save to JSON file
with open('fd_rates_by_tenure.json', 'w') as json_file:
    json.dump(final_rates_by_tenure, json_file, indent=4)

# Example output
for tenure, rates in final_rates_by_tenure.items():
    print(f"{tenure}:")
    for bank, rate in rates.items():
        print(f"  {bank}: {rate}")
