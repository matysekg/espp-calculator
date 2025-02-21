# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import unittest
import requests
import json
from unittest import TestCase
import re
from datetime import datetime
from datetime import timedelta
import pandas as pd
import xlsxwriter
import xlsxwriter.worksheet
import argparse
import sys

def test_always_passes():
    assert True

def test_always_fails():
    assert False

class NbpRatesDm1:
    """Class to obtain and cache USD/PLN reates for needed dates.
    """
    def __init__(self):
        self.rates_cache=dict()

    def get_usd_pln_d_1(self, date: str | datetime) -> float:
        """Returns USD/PLN rate for previous working day before the transaction date
        from NBP. 

        Args:
            date (str | datetime): the transaction date
        
        Returns:
            float: the D-1 USD/PLN rate
        """
        if type(date) == str:
            d = (datetime.strptime(date, "%d.%m.%Y")).date()
        elif type(date) == datetime:
            d = date.date()
        for i in range(1, 7):
            # For Monday we need to move backwards at least 2 days, but Friday could be also bank holiday, Thursday as well
            # assuming no more than 6 non-business day in a raw
            days = timedelta(days=i)
#            get_date = (d - days).strftime('%Y-%m-%d')
            get_date = (d - days).isoformat()
            output = self._get_usd_pln_nbp(get_date)
            if output > 0:
                return float(output)

    def _get_usd_pln_nbp(self, iso_date) -> float:
        """Returns USD/PLN rate for date. The rates are cached, if there is a hit cached value is returned.
        Otherwise rate from NBP is fetched using API

        Args:
            iso_date (bool): date to get the rate for from NBP

        Returns:
            float: the obtained rate
        """
        # http://api.nbp.pl/api/exchangerates/rates/A/USD/2020-06-29/
        # < ExchangeRatesSeries
        # xmlns: xsd = "http://www.w3.org/2001/XMLSchema"
        # xmlns: xsi = "http://www.w3.org/2001/XMLSchema-instance" >
        # < Table > A < / Table >
        # < Currency > dolar
        # amerykański < / Currency >
        # < Code > USD < / Code >
        # < Rates >
        # < Rate >
        # < No > 124 / A / NBP / 2020 < / No >
        # < EffectiveDate > 2020 - 06 - 29 < / EffectiveDate >
        # < Mid > 3.9656 < / Mid >
        # < / Rate >
        # < / Rates >
        # < / ExchangeRatesSeries >
        if iso_date in self.rates_cache.keys():
            rate = self.rates_cache[iso_date]
            #print(f"cached: {iso_date}: {rate}")
            return rate
        else:
            # http://api.nbp.pl/api/exchangerates/rates/A/USD/2020-06-29/
            headers = {'Accept': 'application/json'}
            url = 'http://api.nbp.pl/api/exchangerates/rates/A/USD/'+iso_date
            response = requests.get(url, verify=False, headers=headers)
            if response.ok:
                parse = json.loads(response.text)
                rate = parse['rates'][0]['mid']
                assert(isinstance(rate, (int, float))), "Rate is neither int nor float, wrong data received from API: "\
                                                    + str(rate)
                self.rates_cache[iso_date]=float(rate)
                return float(rate)
            elif response.text == "404 NotFound - Not Found - Brak danych":
                return -1
            else:
                assert False, "Received http error: " + response.text


class SoldItem:
    def __init__(self, sale_type, shares, sale_price, subscription_date, subscription_fmv,
                 purchase_date, purchase_price, purchase_fmv, disposition_type, grant_id,
                 vest_date, vest_fmv, gross_proceeds):
        self.sale_type = sale_type
        self.shares = float(shares)
        self.sale_price = float (sale_price)
        self.subscription_date = datetime.strptime(subscription_date, '%m/%d/%Y')
        self.subscription_fmv = subscription_fmv
        self.purchase_date = datetime.strptime(purchase_date, '%m/%d/%Y')
        self.purchase_price = purchase_price
        self.purchase_fmv = purchase_fmv
        self.disposition_type = disposition_type
        self.grant_id = grant_id
        self.vest_date = datetime.strptime(vest_date, '%m/%d/%Y')
        self.vest_fmv = vest_fmv
        self.gross_proceeds = gross_proceeds
        
class FiscalEvent:
    def __init__(self, input_data):
        if isinstance(input_data, list):
            self._init_with_list(input_data)
        elif isinstance(input_data, dict):
            self._init_with_dict(input_data)
        else:
            raise ValueError("Input data type not supported")    


    def _init_with_list(self, input_line: list):
    #input: ["Date","Action","Symbol","Description","Quantity","Fees & Commissions","Disbursement Election","Amount"]
        header = ["Date","Action","Symbol","Description","Quantity","Fees","Disbursement","Amount"]
        assert(len(input_line) == len(header)), "Incorrect number of Fiscal Event attributes"
        self.event_dict = dict(zip(header,input_line))
        self.event_items_list = []
        #print(f"{input_line}")

        #Here add to dictionary the sale_date_exch_rate_d-1

    def _init_with_dict(self, Transaction: dict):
#       Date, Action, Symbol, Description, Quantity, Fees & Commissions, Disbursement Election, Amount
#           {
        """
        {
            "Date": "08/18/2022",
            "Action": "Sale",
            "Symbol": "CSCO",
            "Quantity": "139.9366",
            "Description": "Share Sale",
            "FeesAndCommissions": "$0.16",
            "DisbursementElection": "Wire Transfer",
            "Amount": "$6,926.00",
            "TransactionDetails": [
                {
                    "Details": {
                        "Type": "RS",
                        "Shares": "6.9366",
                        "SalePrice": "$49.495",
                        "SubscriptionDate": "",
                        "SubscriptionFairMarketValue": "",
                        "PurchaseDate": "",
                        "PurchasePrice": "",
                        "PurchaseFairMarketValue": "",
                        "DispositionType": null,
                        "GrantId": "1430797",
                        "VestDate": "06/10/2021",
                        "VestFairMarketValue": "$54.02",
                        "GrossProceeds": "$343.33"
                    }
                },
                {
                    "Details": {
                        "Type": "ESPP",
                        "Shares": "52.0634",
                        "SalePrice": "$49.495",
                        "SubscriptionDate": "01/04/2021",
                        "SubscriptionFairMarketValue": "$43.96",
                        "PurchaseDate": "06/30/2021",
                        "PurchasePrice": "$37.366",
                        "PurchaseFairMarketValue": "$53.00",
                        "DispositionType": "Disqualified",
                        "GrantId": null,
                        "VestDate": "",
                        "VestFairMarketValue": "",
                        "GrossProceeds": "$2,576.88"
                    }
                },
                {
                    "Details": {
                        "Type": "Div Reinv",
                        "Shares": "1.1708",
                        "SalePrice": "$49.495",
                        "SubscriptionDate": "",
                        "SubscriptionFairMarketValue": "",
                        "PurchaseDate": "10/29/2021",
                        "PurchasePrice": "$56.4832",
                        "PurchaseFairMarketValue": "",
                        "DispositionType": null,
                        "GrantId": null,
                        "VestDate": "",
                        "VestFairMarketValue": "",
                        "GrossProceeds": "$57.95"
                    }
                },
            }
        },
        {
        "Date": "04/27/2022",
        "Action": "Dividend",
        "Symbol": "CSCO",
        "Quantity": null,
        "Description": "Credit",
        "FeesAndCommissions": null,
        "DisbursementElection": null,
        "Amount": "$118.99",
        "TransactionDetails": []
        },
        {
        "Date": "04/27/2022",
        "Action": "Tax Withholding",
        "Symbol": "CSCO",
        "Quantity": null,
        "Description": "Debit",
        "FeesAndCommissions": null,
        "DisbursementElection": null,
        "Amount": "-$17.85",
        "TransactionDetails": []
        },
        """
        Date = Transaction["Date"]
        #Need to convert date to datetime
        Transaction["Date"] = convert_us_string_date_to_datetime(Date)
        for key, value in Transaction.items():
            #Need to trim $ from prices and convert to float
            if key in ["Quantity", "FeesAndCommissions", "Amount"]:
                #sometime empty value is null, sometimes "" -  empty string
                if bool (value):
                    Transaction[key] = convert_us_string_number_to_float(value)
                else: Transaction[key] = 0.00
        self.event_dict={}
        #Information about the transaction is the transaction dict minus "TransactionDetails"
        self.event_dict = {key: value for key, value in Transaction.items() if key != "TransactionDetails"}
        if not self.event_dict['Amount']:
            self.event_dict['Amount'] = 0.00
        #Event_items_list is a list of dicts being values of "Details" key in "TransactionDetails" list of dicts.
        self.event_items_list = []
        for Detail in Transaction['TransactionDetails']:
            #There are some Sell transaction details with shares number  = 0. Ignore them.
            if Transaction['Action'] == "Sale":
                if Detail["Details"]['Shares'] == "0":
                    continue
            event_item={}
            event_item['Date']=Transaction["Date"]
            event_item.update(Detail["Details"])

            """
            "Date": "<sale date> str"
            "Type": "Div Reinv",
            "Shares": "1.1708",
            "SalePrice": "$49.495",
            "SubscriptionDate": "",
            "SubscriptionFairMarketValue": "",
            "PurchaseDate": "10/29/2021",
            "PurchasePrice": "$56.4832",
            "PurchaseFairMarketValue": "",
            "DispositionType": null,
            "GrantId": null,
            "VestDate": "",
            "VestFairMarketValue": "",
            "GrossProceeds": "$57.95"
            """
            #RS are bought at 0$ but this is represented as Null; need to convert to 0.00
            #if event_item["PurchasePrice"] is None:
            #    event_item["PurchasePrice"] = 0.00
            
            for key, value in event_item.items():
                if key in ["Shares", "SalePrice", "GrossProceeds", "PurchasePrice"]:
                    if bool(value) == False: event_item[key] = 0.00
                    else: event_item[key] = convert_us_string_number_to_float(value)
                elif key in ["PurchaseDate", "VestDate"]:
                    #Need to convert dates to datetime; leave empty strings as they are.
                    if bool(value) == True: event_item[key] = convert_us_string_date_to_datetime(value)
            self.event_items_list.append(event_item)

    def add_item(self, header, input_line):
        #print(f"{header}\n{input_line}")
        assert (len(input_line) == len(header)), "Incorrect number of event item attributes"
        event_item=dict(zip(header, input_line))
        # Here add to dictionary the purchase_date_exch_rate_d-1

        self.event_items_list.append(dict(zip(header, input_line)))


#       Date, Action, Symbol, Description, Quantity, Fees & Commissions, Disbursement Election, Amount
#

    def copy_sale_to_its_details(self, sale_rate: float) -> bool:
        """To present sale items itself along with fees for each sale event we need to add to dataframe a row with "Date", "Fee", "Type": "Sell", "Amount", "Shares"
        and all the other Sale Event Item dict keys with empty value.

        Args:
            sale_rate (float): USD price for D-1 of D = FiscalEvent Date 
            fin_event (FiscalEvent): FiscalEvent object containing EventItems

        Returns:
            dict: Original FiscalEvent.event_dict + missing keys/values to have the same keys as modified EventItems 
        """
        event_item_empty = {
                "Type": "Sale",
                "Shares": self.event_dict["Quantity"],
                "SalePrice": 0.00,
                "PurchaseDate": "",
                "PurchasePrice": 0.00,
                "GrossProceeds": 0.00,
                "SaleUSDRate D-1 PLN": sale_rate,
                "PurchaseUSDRate D-1 PLN": 0.00,
                "Amount" : self.event_dict["Amount"],
                "Date": self.event_dict["Date"],
                "FeesAndCommissions" : self.event_dict["FeesAndCommissions"],
                "PurchaseCost PLN" : 0.00
            }
        self.event_items_list.append(event_item_empty)
        return True

def parse_json_to_fiscal_events_list(data: dict) -> list[FiscalEvent]:
    """converts transactions from dictionary to list of FiscalEvent

    Args:
        data (dict): JSON transactions history loaded into dict
        {
        "FromDate": "01/01/2022",
        "ToDate": "12/31/2022",
        "Transactions": [
            {},
            {},
        ]
    }

    Returns:
        list[FiscalEvent]: list of FiscalEvent class objects
    """
    list_of_events=[]
    
    for Transaction in data["Transactions"]:
        #Deposits and Dividend Reinvested purchases are not relevant, skip
        if Transaction["Action"] in ["Deposit","Dividend Reinvested"]:
            continue
        list_of_events.append(FiscalEvent(Transaction))
    return list_of_events

def parse_csv(filename: str):
    """
        This funcion works fine only for data exported to CSV before 2023. Now the CSV structure has changed.
    """   
    list_of_events=[]
    with open(filename, "r+") as file:
        data = file.read()
    events=[]
    data = data.splitlines()
    i = 0
    while i < len(data):
        line = re.sub(r"\$", "", data[i])
        line = re.sub(r"(\d+)\,(\d+)", r"\1\2", line)
        line = line.replace('"', '')
        line = line.split(',')
        #print(f"linia[0]: typ{type(line)}: zaw:{line}")
        ## Check if the first column value is date - if so -> convert it to datetime
        # header, financial event or financial event item
        # financial event item starts from "", and len is gt 1
        # financial event starts from date

        if (bool(line[0]) == False) and (len(line)>1):
            header=line.copy()
            #first and last header column name is empty string, remove them.
            header.pop(0)
            header.pop(-1)
            for k in range(len(header)):
                header[k] = header[k].replace(" ", "")
                k+=1
            i+=1
            line = re.sub(r"\$", "", data[i])
            line = re.sub(r"(\d+)\,(\d+)", r"\1\2", line)
            line = line.replace('"', '')
            line = line.split(',')
            #first and last column values are empty string
            line.pop(0)
            line.pop(-1)
            #list comprehension over slice iterate
            line[:] = [convert_us_string_date_to_datetime(x) for x in line]
            line[:] = [convert_us_string_number_to_float(x) for x in line]
            #copy Date from last event to event_item header / value
            header.insert(0,"Date")
            line.insert(0,list_of_events[-1].event_dict['Date'])
            list_of_events[-1].add_item(header,line)
        else:
            try:
                #Fiscal event starts with a date.
                line[0] = datetime.strptime(line[0], '%m/%d/%Y')
                list_of_events.append(FiscalEvent(line))
            except ValueError as err:
                pass
        i = i+1
    return list_of_events

def convert_us_string_date_to_datetime(input: str):
    return datetime.strptime(input, '%m/%d/%Y')

def convert_us_string_number_to_float(input: str):
    #print(f"Type: {type(input)}, value: {input} ")
    #if string matches int/float format with or without dot then convert it to float.
    #Need to trim $ from prices
    input = re.sub(r"\$","",input)
    #Need to trim k commas from numbers
    input = re.sub(r"(\d),(\d)",r"\1\2",input)
    #numbers as strings need to be converted to floats:
    return float(input)
        #str_precision=f'{strf:.{decimal_places}f}'
        #float_precission = float(str_precision)
        #return float_precission
"""
    {
      "Date": "04/27/2022",
      "Action": "Dividend",
      "Symbol": "CSCO",
      "Quantity": null,
      "Description": "Credit",
      "FeesAndCommissions": null,
      "DisbursementElection": null,
      "Amount": "$118.99",
      "TransactionDetails": []
    },
    {
      "Date": "04/27/2022",
      "Action": "Tax Withholding",
      "Symbol": "CSCO",
      "Quantity": null,
      "Description": "Debit",
      "FeesAndCommissions": null,
      "DisbursementElection": null,
      "Amount": "-$17.85",
      "TransactionDetails": []
    },
"""

def dividend_events_to_pandas(obj_list: list[FiscalEvent], rates: NbpRatesDm1) -> pd.DataFrame:
    """_summary_

    Args:
        obj_list (list[FiscalEvent]): list if FiscalEvents class objects;
        some of them are Dividend and Dividend Tax related
        rates (NbpRatesDm1): object checking and caching D-1 USD/PLN NBP rates 

    Returns:
        pd.DataFrame: Returns pd.DataFrame with table of dividend related events.
    """
    dict_of_divs_dicts={}
    date = datetime(1900,1,1)
    for fin_event in obj_list:
        if fin_event.event_dict["Action"] == "Dividend":
            #take date and amount and put them in dict_of_divs_dicts['Date']['Income USD','DividendDate']
            div_dict={}
            date = fin_event.event_dict['Date']
            if str(date) not in dict_of_divs_dicts.keys(): 
                dict_of_divs_dicts[str(date)] = {}
            amount = fin_event.event_dict['Amount']
            div_dict['DividendDate'] = date
            div_dict['Income USD'] = amount
            dict_of_divs_dicts[str(date)] = dict_of_divs_dicts[str(date)] | div_dict
        elif fin_event.event_dict["Action"] == "Tax Withholding":
            #take date and amount and put it in dict_of_divs_dicts['Date']['Tax Withholding USD']
            date = fin_event.event_dict['Date']
            if str(date) not in dict_of_divs_dicts.keys(): 
                dict_of_divs_dicts[str(date)] = {}
            amount = fin_event.event_dict['Amount']
            dict_of_divs_dicts[str(date)]['TaxWitholded USD'] = amount * -1
        else : continue
    if dict_of_divs_dicts != []:
    #Add USD rate D-1 to all divident events
        for div in dict_of_divs_dicts.values():
            date = div['DividendDate']
            div['DividendUSDRate D-1 PLN'] = rates.get_usd_pln_d_1(date)
        div_df=pd.DataFrame.from_dict(dict_of_divs_dicts,orient = 'index')
        return div_df
    else:
        return pd.DataFrame()



def SaleEventsToPandas(obj_list: list[FiscalEvent], rates: NbpRatesDm1) -> pd.DataFrame:
    """_summary_

    Args:
        obj_list (list[FiscalEvent]): list if FiscalEvents class objects;
        some of them are Sale related and those we process.
        rates (NbpRatesDm1): object checking and caching D-1 USD/PLN NBP rates 

    Returns:
        pd.DataFrame: pd.DataFrame with information related to Sales.
    """
    #Input is a list of FinancialEvent. Output should be pandas dataframe of sale events.
    list_of_sale_df=[]
    sale_rate = 0.00
    for fin_event in obj_list:
        if fin_event.event_dict["Action"] != "Sale":
            continue
        #list=[]
        #list.append(fin_event.event_dict)
        #event_df=pd.DataFrame.from_dict(list)
        #list_of_sale_df.append(event_df)
        #print(f"Sale date: {fin_event.event_dict['Date']:%d.%m.%Y}")
        #for each of event_items dicts add ['PurchaseUSDRate D-1 PLN'] = rates.get_usd_pln_d_1(purchase_date)
        fin_event.event_items_list[:] = [ PurchaseDateRate(x, rates) for x in fin_event.event_items_list ]
        sale_rate = rates.get_usd_pln_d_1(fin_event.event_dict['Date'])
        #for each event_items dicts add ['SaleUSDRate D-1 PLN'] = sale_rate
        fin_event.event_items_list[:] = [ AddSaleRate(x, sale_rate) for x in fin_event.event_items_list ]
        #drop keys/values not needed
        fin_event.event_items_list[:] = [ DropSurplusKeys(x) for x in fin_event.event_items_list ]
        fin_event.event_items_list[:] = [ AddSaleItemMissingKeys(x) for x in fin_event.event_items_list ]
        #Add event_item representing the Fiscal Event type Sale itself - for fee tracking in the same table.
        fin_event.copy_sale_to_its_details(sale_rate)
        #fin_event.event_items_list.append(CreateSaleEventItem(fin_event, sale_rate))
        #Create a dataframe
        sale_df=pd.DataFrame.from_dict(fin_event.event_items_list)
        #Rename columns to be self-explanatory
        sale_df=sale_df.rename(columns={'SalePrice' : 'SalePrice USD', 'Date' : 'SaleDate', 'GrossProceeds' : 'GrossProceeds USD', \
                                        'PurchasePrice' : 'PurchasePrice USD', 'Amount': 'Amount USD', 'FeesAndCommissions': 'FeesAndCommissions USD'})
        list_of_sale_df.append(sale_df)
 #       sale_df['purchase_rate_d-1']=sale_df.apply(lambda x: PurchaseDate(x, rates), axis=1)
        #print(event_df)

    if list_of_sale_df == []:
        #If there are no sales events return and empty DataFrame.
        return pd.DataFrame()
    else:
        return pd.concat(list_of_sale_df)

def CreateSaleEventItem(fin_event: FiscalEvent, sale_rate: float) -> dict:
    """To present sale items itself along with fees for each sale event we need to add to dataframe a row with "Date", "Fee", "Type": "Sell", "Amount", "Shares"
      and all the other Sale Event Item dict keys with empty value.

    Args:
        sale_rate (float): USD price for D-1 of D = FiscalEvent Date 
        fin_event (FiscalEvent): FiscalEvent object containing EventItems

    Returns:
        dict: Original FiscalEvent.event_dict + missing keys/values to have the same keys as modified EventItems 
    """
    event_item_empty = {
            "Type": "Sale",
            "Shares": fin_event.event_dict["Quantity"],
            "SalePrice": 0.00,
            "PurchaseDate": "",
            "PurchasePrice": 0.00,
            "GrossProceeds": 0.00,
            "SaleUSDRate D-1 PLN": sale_rate,
            "PurchaseUSDRate D-1 PLN": 0.00,
            "Amount" : convert_us_string_number_to_float(fin_event.event_dict["Amount"]),
            "Date": fin_event.event_dict["Date"],
            "FeesAndCommissions" : convert_us_string_number_to_float(fin_event.event_dict["FeesAndCommissions"]),
            "PurchaseCost PLN" : 0.00
          }
    return event_item_empty

def AddSaleItemMissingKeys(sale_item: dict) -> dict:
    """Adds to sale item "Fee" and "Amount", so that it can be stored together with Fiscal Event modified dict.

    Args:
        sale_item (dict): Fiscal Event Sale Item dict

    Returns:
        _type_: _description_
    """
    sale_item['FeesAndCommissions'] = 0.00
    sale_item['Amount'] = 0.00
    sale_item['PurchaseCost PLN'] = 0.00
    return sale_item

def AddSaleRate(sale_item: dict, sale_rate: float):
    sale_item['SaleUSDRate D-1 PLN'] = sale_rate
    return sale_item

def PurchaseDateRate(sale_item: dict, rates: NbpRatesDm1):
    #ESPP and Div Reinvestment are purchased at Purchase Date
    #RS are vested at Vest Date
    if sale_item['Type']=="RS":
        sale_item['PurchaseDate'] = sale_item['VestDate']
    purchase_date = sale_item['PurchaseDate']
    sale_item['PurchaseUSDRate D-1 PLN'] = rates.get_usd_pln_d_1(purchase_date)
    return sale_item

def DropSurplusKeys(sale_item: dict):
    sale_item.pop('VestDate')
    sale_item.pop('SubscriptionDate')
    #Old CSV had ...FMV
    if "SubscriptionFMV" in sale_item:
        sale_item.pop('SubscriptionFMV')
        sale_item.pop('PurchaseFMV')
        sale_item.pop('VestFMV')
    elif 'SubscriptionFairMarketValue' in sale_item:
        sale_item.pop('SubscriptionFairMarketValue')
        sale_item.pop('PurchaseFairMarketValue')
        sale_item.pop('VestFairMarketValue')        
    sale_item.pop('DispositionType')
    sale_item.pop('GrantId')
    return sale_item


def PurchaseDate(sale_df: pd.DataFrame, rates: NbpRatesDm1):
    #ESPP and Div Reinvestment are purchased at Purchase Date
    if sale_df['Type']!="RS":
        return rates.get_usd_pln_d_1(sale_df['PurchaseDate'])
    #RS are vested at Vest Date
    else:
        return rates.get_usd_pln_d_1(sale_df['VestDate'])

def add_sales_sums(items: pd.DataFrame) -> pd.DataFrame:
    items['PurchaseCost PLN']=items['Shares']*items['PurchasePrice USD']*items['PurchaseUSDRate D-1 PLN']
    items['GrossProceeds PLN'] = items['Shares'] * items['SalePrice USD'] * items['SaleUSDRate D-1 PLN']
    items['FeesAndCommissions PLN'] = items["FeesAndCommissions USD"]*items["SaleUSDRate D-1 PLN"]
    return items

def calculate_tax(items: pd.DataFrame):
    tax=0.00
    total_cost_pln = items.loc['Total','PurchaseCost PLN'] + items.loc['Total','FeesAndCommissions PLN']
    items.loc['Total','TotalCost PLN']=total_cost_pln
    tax = (items.loc['Total','GrossProceeds PLN'] - total_cost_pln)*0.19
    items.loc['Total','Tax PLN']=tax

def calculate_dividend_tax(items: pd.DataFrame):

    items['Income PLN'] = items['Income USD'] * items['DividendUSDRate D-1 PLN']
    items['TaxWitholdedInUS PLN'] = items['TaxWitholded USD'] * items['DividendUSDRate D-1 PLN']
    items['TaxPL PLN'] = items['Income PLN'].multiply(other=0.19)
    #items.loc[:,'TaxPL PLN'] *= 0.19
    items.loc['Total','Income PLN'] = items['Income PLN'].sum()
    items.loc['Total','TaxWitholdedInUS PLN'] = items['TaxWitholdedInUS PLN'].sum()
    items.loc['Total','TaxPL PLN'] = items['TaxPL PLN'].sum()
    items.loc['Total','TaxDue PLN'] = items.loc['Total','TaxPL PLN'] - items.loc['Total','TaxWitholdedInUS PLN']

def format_xlsx(workbook: xlsxwriter.workbook, excel_out: pd.DataFrame, worksheet: xlsxwriter.worksheet.Worksheet) -> bool:
        #set formatting
        date_dict = {'num_format':'dd-mm-yyyy'}
        date_format = workbook.add_format(date_dict)
        blue_dict = {'bg_color': '#87CEFA', 'font_color': '#000000'} #lightskyblue
        # Define a format object with blue fill
        blue_format = workbook.add_format(blue_dict)
        green_format = workbook.add_format({'bg_color': '#90EE90', 'font_color': '#000000'}) #lightgreen
        lightcyan_dict = {'bg_color': '#E0FFFF', 'font_color': '#000000'} #lightcyan
        lightcyan_format = workbook.add_format(lightcyan_dict)
        # Add a header format.
        header_format_wrapped = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": "#D7E4BC",
                "border": 1,
            }
        )
        header_format_unwrapped = workbook.add_format(
            {
                "bold": True,
                "text_wrap": False,
                "valign": "top",
                "fg_color": "#D7E4BC",
                "border": 1,
            }
        )
        # Rewrite the column headers with the defined format.
        for col_num, value in enumerate(excel_out.columns.values):
            worksheet.write(0, col_num, value, header_format_wrapped)

        # Iterate over the rows of the DataFrame and apply the date format to columns 'PurchaseDate' and 'SaleDate'
        # If the Event Type is "Sale" colour the row to blue.
        # Skip last row as there are no dates there
        for row_num in range(len(excel_out)-1):
            # Write the cell value with dd-mm-yyyy date formatting;
            # Rows with 'Type' == 'Sale' do not have 'PurchaseDate' set.
            # Cells with date have format set already, we need to rewrite it.

            try:
                #For Sale Tax worksheet there is a Type column
                operation_type = excel_out['Type'].iloc[row_num]
            except KeyError:
                #For Dividend Tax worksheet there is no Type column, and we don't apply colour for "Sale" rows.
                #Just format the Date properly.
                operation_type = ""
            if operation_type != "Sale":
                # Apply lightcyan to non-sale rows
                worksheet.set_row(row_num+1, None, lightcyan_format)
                # Iterate over each column and apply the date format to columns containing 'Date' in the name
                for col_num, column_name in enumerate(excel_out.columns):
                    if 'Date' in column_name:
                        # Apply the date format to the column with 'Date' in the name
                        worksheet.write(row_num + 1, col_num, excel_out[column_name].iloc[row_num], workbook.add_format(date_dict | lightcyan_dict))
            else:
                worksheet.set_row(row_num + 1, None, blue_format)  # row_num + 1 to skip the header row; group sale items with level 2
                #for Type: Sale we need to rewite format to blue date for SaleDate.
                worksheet.write(row_num + 1, excel_out.columns.get_loc('SaleDate'), excel_out['SaleDate'].iloc[row_num], \
                                workbook.add_format(date_dict | blue_dict))  # row_num + 1 because of the header row 5 is the index of column 'SaleDate'
        worksheet.set_row(len(excel_out), None, green_format)  # row_num + 1 to skip the header row
        worksheet.autofit()

def format_df_two_decimal_numbers(DF: pd.DataFrame):
    """_summary_

    Args:
        DF (pd.DataFrame): DataFrame with colums with "PLN" but without "Rate" be modified with format: float with two decimal digits. 
    """

    for col_num, column_name in enumerate(DF.columns):
        if 'PLN' in column_name and 'Rate' not in column_name:
            DF[column_name] = DF[column_name].apply(lambda x: float("{:.2f}".format(x)))
    return DF

def add_comments(worksheet: xlsxwriter.worksheet, df: pd.DataFrame, bottom_comments: dict, header_comments: dict = {}):
    """Function that adds comments to named colums in excel sheet last row.

    Args:
        worksheet (xlsxwriter.worksheet): worksheet to insert comments to
        df (pd.DataFrame): data frame to look for given colum location (index) 
        comments (dict): dictionary of {'<column name>':'<comment>'}
    """
    first_row = 1
    if header_comments != {}: 
        for key, value in header_comments.items():
            col_index=df.columns.get_loc(key)
            # Convert the column index to Excel-style alphanumeric column string (e.g., 0 -> 'A', 25 -> 'Z', 26 -> 'AA', etc.)
            col_letter = xlsxwriter.utility.xl_col_to_name(col_index)
            # Construct the cell reference (e.g., 'A1', 'B2', etc.)
            cell_reference = f"{col_letter}{first_row}"  # Adding 2 because Excel is 1-indexed and there's a header row
                # Add a comment to the GrossProceeds PLN sum cell
            worksheet.write_comment(cell_reference, value)

    # Find the last row and last column (considering 0-index)
    last_row = len(df.index) - 1
    for key, value in bottom_comments.items():
        col_index=df.columns.get_loc(key)
        # Convert the column index to Excel-style alphanumeric column string (e.g., 0 -> 'A', 25 -> 'Z', 26 -> 'AA', etc.)
        col_letter = xlsxwriter.utility.xl_col_to_name(col_index)
        # Construct the cell reference (e.g., 'A1', 'B2', etc.)
        cell_reference = f"{col_letter}{last_row + 2}"  # Adding 2 because Excel is 1-indexed and there's a header row
            # Add a comment to the GrossProceeds PLN sum cell
        worksheet.write_comment(cell_reference, value)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert export of previous year transactions from Charles Schwab in JSON format to XLSX")
    parser.add_argument("input_json", help="Name of the input JSON file")
    parser.add_argument("output_xlsx", help="Name of the output XLSX file")
    # Parse arguments
    args = parser.parse_args()

    # Read the JSON file
    try:
        with open(args.input_json, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: The file {args.input_json} was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file {args.input_json} is not a valid JSON file.")
        sys.exit(1)


    rates = NbpRatesDm1()
    fiscal_events_list = parse_json_to_fiscal_events_list(data)
    sale_full_df = SaleEventsToPandas(fiscal_events_list, rates)
    if not sale_full_df.empty:
        sale_full_df = sale_full_df.sort_values(by='SaleDate')
        sale_full_df = add_sales_sums(sale_full_df)
        sale_full_df.loc['Total'] = sale_full_df.filter(items=['PurchaseCost PLN','FeesAndCommissions PLN', \
                                                            'GrossProceeds PLN']).sum(numeric_only=True)
        calculate_tax(sale_full_df)
        format_df_two_decimal_numbers(sale_full_df)
    dividend_df = dividend_events_to_pandas(fiscal_events_list, rates)
    if not dividend_df.empty:
        calculate_dividend_tax(dividend_df)
        format_df_two_decimal_numbers(dividend_df)
    print(f'\n{sale_full_df}\n')
    print(f'\n{dividend_df}\n')

#    dividend_df = calculate_dividend_tax(dividend_df)
#    print(f'\n{sale_full_df}\n')
    with pd.ExcelWriter(args.output_xlsx, datetime_format='MM/DD/YYYY', engine='xlsxwriter') as writer:
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



class TestNbpRatesDm1(unittest.TestCase):

    def test_get_usd_pln_d_1_cached(self):
        rates = NbpRatesDm1()
        date = (datetime.strptime("12/07/2020", "%m/%d/%Y")).date()
        rates.rates_cache[(date.isoformat())] = 3.9646
        # http://api.nbp.pl/api/exchangerates/rates/A/USD/2020-07-12/
        # due to Sunday expected d-1 = http://api.nbp.pl/api/exchangerates/rates/A/USD/2020-07-10/
        expected = 3.9646
        self.assertEqual(rates.get_usd_pln_d_1("12/07/2020"), expected)

    def test_get_usd_pln_nbp(self):
        rates = NbpRatesDm1()
        expected_value = 3.9656
        result = rates.get_usd_pln_nbp("2020-06-29")
        self.assertEqual(result, expected_value)

    def test_get_usd_pln_nbp_404(self):
        # Check if function properly raises exception if it gets "wrong" 404.
        rates = NbpRatesDm1()
        self.assertRaises(AssertionError, rates.get_usd_pln_nbp("20210-06-29"))



def ConvDate(input: pd.DataFrame):
    for name, values in input[['PurchaseDate','VestDate','SubscriptionDate']].items():
        #if not empty
        if bool(values) == True:
            input[name] = datetime.strptime(values, '%m/%d/%Y')
        #print(f"{input[name]}")
    return input
        #date = datetime.strptime(date, '%m/%d/%Y')
        #print(f'{date.day}.{date.month}.{date.year}')

def ConvDate(input: str):
    line=input.split()
    line[:]=[datetime.strptime(date, '%m/%d/%Y') for date in line]
    return line