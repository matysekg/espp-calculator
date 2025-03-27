#!/bin/python3

import mainjson
from js import alert

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


def error_handler(e):
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        lineno = exception_traceback.tb_lineno

        msg  = 'Exception Type: ' + str(exception_type) + '\n'
        msg += 'File: ' + filename + '\n'
        msg += 'Line: ' + str(lineno) + '\n'
        msg += 'Error: ' + str(e)

        print(msg)
        alert(msg)

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
        await download_json(dictionary)
    else:
        pprint("No file selected.")


async def main():
    #
    rates = mainjson.NbpRatesDm1()

    fiscal_events_list = mainjson.parse_json_to_fiscal_events_list(data)
    sale_full_df = mainjson.SaleEventsToPandas(fiscal_events_list, rates)
    if not sale_full_df.empty:
        sale_full_df = sale_full_df.sort_values(by='SaleDate')
        sale_full_df = mainjson.add_sales_sums(sale_full_df)
        sale_full_df.loc['Total'] = sale_full_df.filter(items=['PurchaseCost PLN','FeesAndCommissions PLN', \
                                                            'GrossProceeds PLN']).sum(numeric_only=True)
        mainjson.calculate_tax(sale_full_df)
        mainjson.format_df_two_decimal_numbers(sale_full_df)
    dividend_df = mainjson.dividend_events_to_pandas(fiscal_events_list, rates)
    if not dividend_df.empty:
        mainjson.calculate_dividend_tax(dividend_df)
        mainjson.format_df_two_decimal_numbers(dividend_df)
    print(f'\n{sale_full_df}\n')
    print(f'\n{dividend_df}\n')

#    dividend_df = calculate_dividend_tax(dividend_df)
#    print(f'\n{sale_full_df}\n')
"""
    with mainjson.pd.ExcelWriter(args.output_xlsx, datetime_format='MM/DD/YYYY', engine='xlsxwriter') as writer:
        # Access the xlsxwriter workbook object
        workbook  = writer.book

        if not sale_full_df.empty:
            excel_out = sale_full_df[['Type', 'Shares', 'PurchaseDate', 'PurchasePrice USD', 'PurchaseUSDRate D-1 PLN', 'SaleDate', 'SalePrice USD', \
                        'GrossProceeds USD', 'Amount USD','FeesAndCommissions USD', 'SaleUSDRate D-1 PLN', 'PurchaseCost PLN', 'FeesAndCommissions PLN', 'GrossProceeds PLN', \
                            'TotalCost PLN', 'Tax PLN' ]]
            # Write the DataFrame to the Excel file
            excel_out.to_excel(writer, index=False, sheet_name='Sale Tax')
            
            # Access the xlsxwriter worksheet object
            worksheet = writer.sheets['Sale Tax']
            #instruct user which cells should be put into which field of Pit38(2023)
            header_comments = {
                'PurchaseCost PLN':'= Shares * PurchasePrice USD * PurchaseUSDRate D-1 PLN',
                'FeesAndCommissions PLN':'= FeesAndCommissions USD * SaleUSDRate D-1 PLN',
                'GrossProceeds PLN': '= GrossProceeds USD * SaleUSDRate D-1 PLN',
                'TotalCost PLN': '= sum(PurchaseCost PLN) + sum(FeesAndCommissions PLN)',
                'Tax PLN': '= ( sum(GrossProceeds PLN) - TotalCost PL ) * 0,19'
            }
            bottom_comments = {
                'GrossProceeds PLN':'Into Pit38 C.22', # Add a comment to the GrossProceeds PLN sum cell 
                'TotalCost PLN':'Into Pit38 C.23' # Add a comment to the TotalCost PLN cell
                }

            add_comments(worksheet,excel_out, bottom_comments=bottom_comments, header_comments=header_comments)
            #make sure dates are disaplayed correctly, and the table is easy to read.
            format_xlsx(workbook, excel_out, worksheet)
        else:
            print("There were no sale transactions.")
        if not dividend_df.empty:
            #add dividend calculations sheet
            dividend_df.to_excel(writer, index=False, sheet_name='Dividend Tax')
            # Access the xlsxwriter worksheet object

            worksheet = writer.sheets['Dividend Tax']
            #instruct user which cells should be put into which field of Pit38(2023)
            header_comments = {
                'Income PLN': '= Income USD * DividendUSDRate D-1 PLN',
                'TaxWitholdedInUS PLN': '= TaxWitholded USD * DividendUSDRate D-1 PLN',
                'TaxPL PLN': '= Income PLN * 0,19',
                'TaxDue PLN': '= sum(TaxPL PLN) - sum(TaxWitholdedInUS PLN)'
                }
            bottom_comments = {
                'TaxWitholdedInUS PLN':'Into Pit38 G.46', # Add a comment to the GrossProceeds PLN sum cell 
                'TaxPL PLN':'Into Pit38 G.45' # Add a comment to the TotalCost PLN cell
                }
            add_comments(worksheet, dividend_df, header_comments=header_comments, bottom_comments=bottom_comments)
            #make sure dates are disaplayed correctly, and the table is easy to read.
            format_xlsx(workbook, dividend_df, worksheet)
        else:
            print("There were no dividends received.")

"""
    #Run the main:
try:
    await main()
except Exception as e:
    error_handler(e)