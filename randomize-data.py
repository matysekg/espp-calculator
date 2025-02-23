import json
import random
from pyscript import document, window
from js import Blob, document, URL
#import asyncio
from pyodide.ffi.wrappers import add_event_listener
from pprint import pprint

# Function to process transactions
def randomize_dividends(data):
    for transaction in data["Transactions"]:
        if transaction["Action"] == "Dividend" and transaction["Amount"]:
            # Randomize the "Amount" for Dividend transactions
            original_amount = float(transaction["Amount"].replace("$", "").replace(",", ""))
            new_amount = round(random.uniform(0.05, 10)  * original_amount, 2)
            transaction["Amount"] = f"${new_amount:,.2f}"

            # Find the corresponding "Tax Withholding" transaction
            for tax_transaction in data["Transactions"]:
                if (tax_transaction["Action"] == "Tax Withholding" and
                        tax_transaction["Date"] == transaction["Date"]):
                    tax_amount = round(0.15 * new_amount, 2)
                    tax_transaction["Amount"] = f"-${tax_amount:,.2f}"
                    break

            # Find the corresponding "Dividend Reinvested" transaction
            for reinvest_transaction in data["Transactions"]:
                if (reinvest_transaction["Action"] == "Dividend Reinvested" and
                        reinvest_transaction["Date"] == transaction["Date"]):
                    reinvest_amount = round(0.85 * new_amount, 2)
                    reinvest_transaction["Amount"] = f"-${reinvest_amount:,.2f}"
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
    return data

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
                    new_shares = round(random.uniform(0.05, 10)  * original_shares, 4)
                    details["Shares"] = f"{new_shares}"
                    
                    # Calculate new GrossProceeds
                    sale_price = float(details["SalePrice"].replace("$", "").replace(",", ""))
                    gross_proceeds = round(new_shares * sale_price, 2)
                    details["GrossProceeds"] = f"${gross_proceeds:,.2f}"

                    # Sum up total quantity
                    total_quantity += new_shares

            # Update the overall Quantity and Amount for the Sale transaction
            transaction["Quantity"] = f"{round(total_quantity, 4)}"
            if sale_price is not None:
                transaction["Amount"] = f"${round(total_quantity * sale_price, 2):,.2f}"
    return data


def randomize_deposits(data):
    for transaction in data["Transactions"]:
        if transaction["Action"] == "Deposit":
            # Randomize the Quantity
            original_quantity = float(transaction["Quantity"])
            new_quantity = round(random.uniform(0.05, 10)  * original_quantity, 4)
            transaction["Quantity"] = f"{new_quantity}"
            
            # Update the Amount only if it's not null
            if transaction["Amount"] is not None:
                # Iterate over TransactionDetails to calculate the new amount
                for detail in transaction["TransactionDetails"]:
                    details = detail["Details"]
                    if "PurchasePrice" in details:
                        purchase_price = float(details["PurchasePrice"].replace("$", "").replace(",", ""))
                        # Calculate the new amount based on Quantity and Purchase Price
                        new_amount = round(new_quantity * purchase_price, 2)
                        transaction["Amount"] = f"${new_amount:,.2f}"
    return data

def randomize_wire_transfers(data):
    for transaction in data["Transactions"]:
        if transaction["Action"] == "Wire Transfer":
            # Randomize the Amount if it is not null or empty
            if transaction["Amount"] not in (None, ""):
                # Remove the dollar sign and commas, then convert to float
                original_amount = float(transaction["Amount"].replace("$", "").replace(",", ""))
                # Randomize the Amount, preserving the sign
                sign = "-" if original_amount < 0 else ""
                new_amount = round(random.uniform(0.05, 10) * abs(original_amount), 2)
                # Format the new amount with a dollar sign and two decimal places
                pprint(f"new amount: {f'{sign}${new_amount:,.2f}'}")
                transaction["Amount"] = f"{sign}${new_amount:,.2f}"

    return data

def read_file_content(content):
    try:
        data_dict = json.loads(content)
        # Print the dictionary to the console
        print(data_dict)
        # Display the dictionary on the webpage
        document.getElementById("output").innerText = str(data_dict)
    except json.JSONDecodeError:
        document.getElementById("output").innerText = "Invalid JSON file."

async def download_json(data, filename='randomized_data.json'):
    # Convert the data to a JSON string
    json_data = json.dumps(data, indent=4)
    '''
    try:
        options = {
			"startIn": "documents",
			"suggestedName": "randomized_data.json"
		}
        fileHandle = await window.showSaveFilePicker({"suggestedNameeeee": "random.json"})
    except Exception as e:
        pprint('Exception: ' + str(e))
        return

    file = await fileHandle.createWritable()
    await file.write(json_data)
    await file.close()
    return
    '''
    # content is the data to write to a file
    tag = document.createElement('a')
    blob = Blob.new([json_data], {type: "text/json"})
    tag.href = URL.createObjectURL(blob)
    tag.download = filename
    tag.click()
    return

async def upload_file_and_process(e):

    # Get the target of the event
    target = e.target
    jsonFile = document.querySelector('#jsonFile')
    '''    # Iterate over the properties of the target
    attributes = dir(jsonFile)  # Using dir() to get a list of attributes
    for attr in attributes:
        try:
            # Attempt to print the attribute and its value
            print(f"{attr}: {getattr(target, attr)}")
        except Exception as ex:
            # Handle any exceptions (e.g., accessing certain properties might throw errors)
            print(f"Could not access {attr}: {ex}")'''

    file_list = jsonFile.files
    if file_list.length > 0:
        # Get the first file
        first_file = file_list.item(0)
        # Print the name of the file
        print("File name:", first_file.name)
        text = await first_file.text()
        #print(f"File text: {text}" )
        dictionary = json.loads(text)
        #pprint(f"json: {dictionary["Transactions"]}")
        dictionary=randomize_sales(dictionary)
        dictionary=randomize_dividends(dictionary)
        dictionary=randomize_deposits(dictionary)
        dictionary=randomize_wire_transfers(dictionary)
        #pprint(f"json radnomised: {dictionary}")
        await download_json(dictionary)
    else:
        pprint("No file selected.")
    


# Add an event listener to the show active sessions checkbox
upload_button = document.querySelector('#uploadButton')
add_event_listener(upload_button,'click', upload_file_and_process)