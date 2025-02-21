import random

# Example data
data = {
    "FromDate": "01/01/2023",
    "ToDate": "12/31/2023",
    "Transactions": [
        {
            "Date": "12/13/2023",
            "Action": "Deposit",
            "Symbol": "CSCO",
            "Quantity": "20",
            "Description": "RS",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": None,
            "TransactionDetails": [
                {
                    "Details": {
                        "AwardDate": "06/09/2022",
                        "AwardId": "1563265",
                        "VestDate": "12/10/2023",
                        "VestFairMarketValue": "$48.38"
                    }
                }
            ]
        },
        {
            "Date": "10/25/2023",
            "Action": "Dividend",
            "Symbol": "CSCO",
            "Quantity": None,
            "Description": "Credit",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": "$135.40",
            "TransactionDetails": []
        },
        {
            "Date": "10/25/2023",
            "Action": "Tax Withholding",
            "Symbol": "CSCO",
            "Quantity": None,
            "Description": "Debit",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": "-$20.31",
            "TransactionDetails": []
        },
        {
            "Date": "10/25/2023",
            "Action": "Dividend Reinvested",
            "Symbol": "CSCO",
            "Quantity": None,
            "Description": "Debit",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": "-$115.09",
            "TransactionDetails": []
        },
        {
            "Date": "10/25/2023",
            "Action": "Deposit",
            "Symbol": "CSCO",
            "Quantity": "2.2254",
            "Description": "Div Reinv",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": None,
            "TransactionDetails": [
                {
                    "Details": {
                        "PurchasePrice": "$51.7154"
                    }
                }
            ]
        },
    ]
}

# Function to process transactions
def process_transactions(data):
    for transaction in data["Transactions"]:
        if transaction["Action"] == "Dividend" and transaction["Amount"]:
            # Randomize the "Amount" for Dividend transactions
            original_amount = float(transaction["Amount"].replace("$", "").replace(",", ""))
            new_amount = round(random.uniform(0.1, 2) * original_amount, 2)
            transaction["Amount"] = f"${new_amount}"

            # Find the corresponding "Tax Withholding" transaction
            for tax_transaction in data["Transactions"]:
                if (tax_transaction["Action"] == "Tax Withholding" and
                        tax_transaction["Date"] == transaction["Date"]):
                    tax_amount = round(0.15 * new_amount, 2)
                    tax_transaction["Amount"] = f"-${tax_amount}"
                    break

            # Find the corresponding "Dividend Reinvested" transaction
            for reinvest_transaction in data["Transactions"]:
                if (reinvest_transaction["Action"] == "Dividend Reinvested" and
                        reinvest_transaction["Date"] == transaction["Date"]):
                    reinvest_amount = round(0.85 * new_amount, 2)
                    reinvest_transaction["Amount"] = f"-${reinvest_amount}"
                    break

            # Find the corresponding "Deposit" transaction and update "Quantity"
            for deposit_transaction in data["Transactions"]:
                if (deposit_transaction["Action"] == "Deposit" and
                        deposit_transaction["Date"] == transaction["Date"]):
                    for detail in deposit_transaction["TransactionDetails"]:
                        if "PurchasePrice" in detail["Details"]:
                            purchase_price = float(detail["Details"]["PurchasePrice"].replace("$", "").replace(",", ""))
                            deposit_quantity = round(reinvest_amount / purchase_price, 4)
                            deposit_transaction["Quantity"] = f"{deposit_quantity}"
                            break

# Apply the function
process_transactions(data)

# Output the modified data
#for transaction in data["Transactions"]:
    #print(transaction)


def randomize_sales(data):
    for transaction in data["Transactions"]:
        if transaction["Action"] == "Sale":
            total_quantity = 0
            sale_price = None

            for detail in transaction["TransactionDetails"]:
                details = detail["Details"]

                if "Shares" in details and "SalePrice" in details:
                    # Randomize shares
                    original_shares = float(details["Shares"])
                    new_shares = round(random.uniform(0.1, 2) * original_shares, 4)
                    details["Shares"] = f"{new_shares}"
                    
                    # Calculate new GrossProceeds
                    sale_price = float(details["SalePrice"].replace("$", "").replace(",", ""))
                    gross_proceeds = round(new_shares * sale_price, 2)
                    details["GrossProceeds"] = f"${gross_proceeds}"

                    # Sum up total quantity
                    total_quantity += new_shares

            # Update the overall Quantity and Amount for the Sale transaction
            transaction["Quantity"] = f"{round(total_quantity, 4)}"
            if sale_price is not None:
                transaction["Amount"] = f"${round(total_quantity * sale_price, 2)}"

# Example data update
data = {
    "Transactions": [
        {
        "Date": "10/17/2023",
        "Action": "Sale",
        "Symbol": "CSCO",
        "Quantity": "93.1643",
        "Description": "Share Sale",
        "FeesAndCommissions": "$0.05",
        "DisbursementElection": None,
        "Amount": "$4,976.86",
        "TransactionDetails": [
            {
            "Details": {
                "Type": "ESPP",
                "Shares": "0.1643",
                "SalePrice": "$53.4208",
                "SubscriptionDate": "01/04/2021",
                "SubscriptionFairMarketValue": "$43.96",
                "PurchaseDate": "06/30/2022",
                "PurchasePrice": "$36.244",
                "PurchaseFairMarketValue": "$42.64",
                "DispositionType": "Qualified",
                "GrantId": None,
                "VestDate": "",
                "VestFairMarketValue": "",
                "GrossProceeds": "$8.78"
            }
            },
            {
            "Details": {
                "Type": "ESPP",
                "Shares": "33.8357",
                "SalePrice": "$53.4208",
                "SubscriptionDate": "01/04/2021",
                "SubscriptionFairMarketValue": "$43.96",
                "PurchaseDate": "06/30/2022",
                "PurchasePrice": "$36.244",
                "PurchaseFairMarketValue": "$42.64",
                "DispositionType": "Qualified",
                "GrantId": None,
                "VestDate": "",
                "VestFairMarketValue": "",
                "GrossProceeds": "$1,807.53"
            }
            },
            {
            "Details": {
                "Type": "Div Reinv",
                "Shares": "1.1643",
                "SalePrice": "$53.4208",
                "SubscriptionDate": "",
                "SubscriptionFairMarketValue": "",
                "PurchaseDate": "10/28/2022",
                "PurchasePrice": "$44.9465",
                "PurchaseFairMarketValue": "",
                "DispositionType": None,
                "GrantId": None,
                "VestDate": "",
                "VestFairMarketValue": "",
                "GrossProceeds": "$62.20"
            }
            },
            {
            "Details": {
                "Type": "ESPP",
                "Shares": "58",
                "SalePrice": "$53.4208",
                "SubscriptionDate": "07/01/2022",
                "SubscriptionFairMarketValue": "$42.60",
                "PurchaseDate": "12/30/2022",
                "PurchasePrice": "$36.21",
                "PurchaseFairMarketValue": "$47.64",
                "DispositionType": "Disqualified",
                "GrantId": None,
                "VestDate": "",
                "VestFairMarketValue": "",
                "GrossProceeds": "$3,098.41"
            }
            }
        ]
        }
    ]
}

# Apply the function
#randomize_sales(data)

# Output the modified data
#for transaction in data["Transactions"]:
#    print(transaction)


def randomize_deposits(data):
    for transaction in data["Transactions"]:
        if transaction["Action"] == "Deposit":
            # Randomize the Quantity
            original_quantity = float(transaction["Quantity"])
            new_quantity = round(random.uniform(0.1, 2) * original_quantity, 4)
            transaction["Quantity"] = f"{new_quantity}"
            
            # If there is an Amount field that depends on Quantity, calculate it
            # Example: Amount might be the quantity multiplied by a price from details
            for detail in transaction["TransactionDetails"]:
                details = detail["Details"]
                if "PurchasePrice" in details:
                    purchase_price = float(details["PurchasePrice"].replace("$", "").replace(",", ""))
                    # Calculate the new amount based on Quantity and Purchase Price
                    new_amount = round(new_quantity * purchase_price, 2)
                    transaction["Amount"] = f"${new_amount}"

# Example data update
data = {
    "Transactions": [
        {
            "Date": "12/13/2023",
            "Action": "Deposit",
            "Symbol": "CSCO",
            "Quantity": "20",
            "Description": "RS",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": None,
            "TransactionDetails": [
                {
                    "Details": {
                        "AwardDate": "06/09/2022",
                        "AwardId": "1563265",
                        "VestDate": "12/10/2023",
                        "VestFairMarketValue": "$48.38"
                    }
                }
            ]
        },
        {
            "Date": "07/01/2022",
            "Action": "Deposit",
            "Symbol": "CSCO",
            "Quantity": "73",
            "Description": "ESPP",
            "FeesAndCommissions": None,
            "DisbursementElection": None,
            "Amount": None,
            "TransactionDetails": [
                {
                    "Details": {
                        "PurchaseDate": "06/30/2022",
                        "PurchasePrice": "$36.244",
                        "SubscriptionDate": "01/04/2021",
                        "SubscriptionFairMarketValue": "$43.96",
                        "PurchaseFairMarketValue": "$42.64"
                    }
                }
            ]
        },
        # More transactions...
    ]
}

# Apply the function
randomize_deposits(data)

# Output the modified data
for transaction in data["Transactions"]:
    print(transaction)