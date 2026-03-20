#!/bin/python3
import json
import mainjson
#import sys
#import io
import base64
from pyscript import document, window
from js import alert,Blob, document, URL, File, Uint8Array
from pyodide.ffi.wrappers import add_event_listener
from pprint import pprint


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
            sale_html = sale_full_df.to_html(classes='data-table', border=1, na_rep='')
            dividend_html = dividend_df.to_html(classes='data-table', border=1, na_rep='')

            # Insert HTML tables into the webpage
            document.getElementById("saleTable").innerHTML = sale_html
            document.getElementById("dividendTable").innerHTML = dividend_html

            #Create a file and a download URL
            data = excel_file.read()
            base64_encoded = base64.b64encode(data).decode('UTF-8')
            octet_string = "data:application/octet-stream;base64,"
            download_string = octet_string + base64_encoded

            #print(f"Download string: \n{download_string}")
            
            #Handle case where two json files are handled one after another
            #If the <a> with id "downloadLink" exists, then delete it first
            hidden_link = document.getElementById("downloadLink")
            if str(type(hidden_link)) != "<class 'pyodide.ffi.JsNull'>":
                document.body.removeChild(hidden_link)

            #Set the default filename to be <json_file>.json
            json_filename = first_file.name
            xlsx_filename = json_filename.replace(".json", ".xlsx")
            hidden_link = document.createElement("a")
            hidden_link.setAttribute("download", xlsx_filename)
            hidden_link.setAttribute("href", download_string)
            hidden_link.id = "downloadLink"
            #deactivate "Process the file" button
            upload_button = document.querySelector('#uploadButton')
            upload_button.disabled = True
            #Activate download button
            document.getElementById("downloadButton").disabled = False
            document.body.appendChild(hidden_link)


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
        #keep only useful columns and set them in the desired order
        sale_df = sale_full_df[[
            'Type', 'Shares', 'PurchaseDate', 'PurchasePrice USD', 'PurchaseUSDRate D-1 PLN',
            'SaleDate', 'SalePrice USD', 'GrossProceeds USD', 'Amount USD', 'FeesAndCommissions USD',
            'SaleUSDRate D-1 PLN', 'PurchaseCost PLN', 'FeesAndCommissions PLN', 'GrossProceeds PLN',
            'TotalCost PLN', 'Tax PLN'
            ]]
    dividend_df = await mainjson.dividend_events_to_pandas(fiscal_events_list, rates)
    if not dividend_df.empty:
        mainjson.calculate_dividend_tax(dividend_df)
        mainjson.format_df_two_decimal_numbers(dividend_df)
        #keep only useful columns and set them in the desired order
        dividend_df=dividend_df[[
            'DividendDate', 'Income USD', 'TaxWitholded USD', 'DividendUSDRate D-1 PLN', 
            'Income PLN', 'TaxPL PLN', 'TaxWitholdedInUS PLN', 'TaxDue PLN'
            ]]
    print(f'\n{sale_df}\n')
    print(f'\n{dividend_df}\n')

    excel_file = mainjson.generate_tax_report(sale_df, dividend_df)

    output = [sale_full_df, dividend_df, excel_file]
    return output


file_select = document.getElementById("jsonFile")
file_select.disabled = False

upload_button = document.querySelector('#uploadButton')


async def handle_file_select(e):
    '''
    If the file select changed check if a files is selected.
    If files is selected activate the upload ("Process the file") button.  
    '''
    #Dectivate download button
    document.getElementById("downloadButton").disabled = True
    #jsonFile = document.querySelector('#jsonFile')
    #print(f"ID of jsonFile: {jsonFile.id}")
    file_select = e.target
    file_list = file_select.files
    if file_list.length > 0:
        filename  = file_list.item(0).name          
        # You can also check if the file is a JSON file (optional)
        extensions = ['json']
        file_extension = filename.split('.').pop().lower()
        
        if file_extension in extensions:
            print("Selected file has a JSON extension:", filename)
        else:
            print("Selected file doesn't have JSON extension:", filename)
        #Activate "Process the file" button
        upload_button = document.querySelector('#uploadButton')
        upload_button.disabled = False

    else:
        print("No file selected")
  



add_event_listener(file_select,'change', handle_file_select)
add_event_listener(upload_button,'click', upload_file_and_process)

def downloadFile(*args):
    hidden_link = document.getElementById("downloadLink")
    hidden_link.click()



add_event_listener(document.getElementById("downloadButton"), "click", downloadFile)

print("Initialisation done")