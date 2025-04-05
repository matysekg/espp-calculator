#!/bin/python3
import json
import mainjson
import sys
from pyscript import document, window
from js import alert,Blob, document, URL
from pyodide.ffi.wrappers import add_event_listener
from pprint import pprint
import io

def read_file_content(content):
    try:
        data_dict = json.loads(content)
        # Print the dictionary to the console
        print(data_dict)
        # Display the dictionary on the webpage
        document.getElementById("output").innerText = str(data_dict)
    except json.JSONDecodeError:
        document.getElementById("output").innerText = "Invalid JSON file."

async def upload_file_and_process(e):

    try:
        jsonFile = document.querySelector('#jsonFile')

        file_list = jsonFile.files
        if file_list.length > 0:
            # Get the first file
            first_file = file_list.item(0)
            # Print the name of the file
            print("File name:", first_file.name)
            text = await first_file.text()
            #print(f"File text: {text}" )
            data = json.loads(text)
            #pprint(f"json: {dictionary["Transactions"]}")
            sale_full_df, dividend_df, excel_file = await main(data)
            # Convert DataFrames to HTML tables
            sale_html = sale_full_df.to_html(classes='data-table', border=1)
            dividend_html = dividend_df.to_html(classes='data-table', border=1)

            # Insert HTML tables into the webpage
            document.getElementById("saleTable").innerHTML = sale_html
            document.getElementById("dividendTable").innerHTML = dividend_html
        else:
            document.getElementById("output").innerText = "No file selected."
    except Exception as e:
        document.getElementById("output").innerText = f"An error occurred: {str(e)}"



async def main(data: dict):
    #
    rates = mainjson.NbpRatesDm1()

    fiscal_events_list = mainjson.parse_json_to_fiscal_events_list(data)
    sale_full_df = await mainjson.SaleEventsToPandas(fiscal_events_list, rates)
    if not sale_full_df.empty:
        sale_full_df = sale_full_df.sort_values(by='SaleDate')
        sale_full_df = mainjson.add_sales_sums(sale_full_df)
        sale_total = sale_full_df.filter(items=['PurchaseCost PLN','FeesAndCommissions PLN', \
                                                            'GrossProceeds PLN'])
        totals = sale_total.sum(numeric_only=True)
#        sale_full_df.loc['Total'] = sale_full_df.filter(items=['PurchaseCost PLN','FeesAndCommissions PLN', \
#                                                            'GrossProceeds PLN']).sum(numeric_only=True)
        # Add totals row to sale_full_df
        sale_full_df.loc['Total', totals.index] = totals.values

        # Optionally fill NaN in other columns for 'Total' row with default values
        #sale_full_df.fillna({'SaleDate': '', 'Type': '', 'Shares': 0, 'SalePrice USD': 0, 'PurchaseDate': '', 'PurchasePrice USD': 0,
        #                     'GrossProceeds USD': 0, 'PurchaseUSDRate D-1 PLN': 0, 'SaleUSDRate D-1 PLN': 0, 'FeesAndCommissions USD': 0,
        #                     'Amount USD': 0, 'TotalCost PLN': 0}, inplace=True)
        #sale_full_df.fillna('',inplace=True)
        mainjson.calculate_tax(sale_full_df)
        mainjson.format_df_two_decimal_numbers(sale_full_df)
    dividend_df = await mainjson.dividend_events_to_pandas(fiscal_events_list, rates)
    if not dividend_df.empty:
        mainjson.calculate_dividend_tax(dividend_df)
        mainjson.format_df_two_decimal_numbers(dividend_df)
    print(f'\n{sale_full_df}\n')
    print(f'\n{dividend_df}\n')

    excel_file = mainjson.generate_tax_report(sale_full_df, dividend_df)

    output = [sale_full_df, dividend_df, excel_file]
    return output

# Add an event listener to the show active sessions checkbox
upload_button = document.querySelector('#uploadButton')
add_event_listener(upload_button,'click', upload_file_and_process)