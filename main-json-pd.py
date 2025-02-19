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
import numpy as np

def test_always_passes():
    assert True

def test_always_fails():
    assert False

class TestGetUsdPlnNbp(unittest.TestCase):

    def test_get_usd_pln_nbp(self):
        expected_value = 3.9656
        result = get_usd_pln_nbp("2020-06-29")
        self.assertEqual(result, expected_value)

    def test_get_usd_pln_nbp_404(self):
        # Check if function properly raises exception if it gets "wrong" 404.
        self.assertRaises(AssertionError, get_usd_pln_nbp, "20210-06-29")


class TestGetUsdPlNbpDayMinus1(unittest.TestCase):

    def test_get_usd_pln_d_1(self):
        # http://api.nbp.pl/api/exchangerates/rates/A/USD/2020-07-12/
        # due to Sunday expected d-1 = http://api.nbp.pl/api/exchangerates/rates/A/USD/2020-07-10/
        expected = 3.9646
        self.assertEqual(get_usd_pln_d_1("12/07/2020"), expected)




def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

class NbpRatesDm1:
    def __init__(self):
        self.rates_cache=dict()

    def get_usd_pln_d_1(self, date: [str, datetime]):
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
            output = self.get_usd_pln_nbp(get_date)
            if output > 0:
                return float(output)

    def get_usd_pln_nbp(self, iso_date):
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
            self.init_with_list(input_data)
        elif isinstance(input_data, dict):
            self.init_with_dict(input_data)
        else:
            raise ValueError("Input data type not supported")
            
    def init_with_list(self, input_line: list):
    #input: ["Date","Action","Symbol","Description","Quantity","Fees & Commissions","Disbursement Election","Amount"]
        header = ["Date","Action","Symbol","Description","Quantity","Fees","Disbursement","Amount"]
        assert(len(input_line) == len(header)), "Incorrect number of Fiscal Event attributes"
        self.event_dict = dict(zip(header,input_line))
        self.event_items_list = []
        #print(f"{input_line}")

        #Here add to dictionary the sale_date_exch_rate_d-1

    def add_item(self, header, input_line):
        #print(f"{header}\n{input_line}")
        assert (len(input_line) == len(header)), "Incorrect number of event item attributes"
        event_item=dict(zip(header, input_line))
        # Here add to dictionary the purchase_date_exch_rate_d-1

        self.event_items_list.append(dict(zip(header, input_line)))

    def init_with_dict(self, Transaction: dict):
#       Date, Action, Symbol, Description, Quantity, Fees & Commissions, Disbursement Election, Amount
#           {
        """
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
                {...}
            } 
        """
        self.event_dict={}
        #Information about the transaction is the transaction dict minus "TransactionDetails"
        self.event_dict = {key: value for key, value in Transaction.items if key != "TransactionDetails"}
        #Event_items_list is a list of dicts being values of "Details" key in "TransactionDetails" list of dicts.
        self.event_items_list = []
        for Detail in Transaction['TransactionDetails']:
            event_item=Detail["Details"]
            self.event_items_list.append(event_item)

def parse_json(filename: str):
    list_of_events=[]
    with open(filename, 'r') as file:
        data = json.load(file)
    """ 
    {
        "FromDate": "01/01/2022",
        "ToDate": "12/31/2022",
        "Transactions": [
            {},
            {},
        ]
    }
    """
    for Transaction in data["Transactions"]:
        Date = Transaction["Date"]
        Transaction["Date"]=datetime.strptime(Date, '%m/%d/%Y')
        list_of_events.append(FiscalEvent(Transaction))
    return list_of_events

def parse_csv(filename: str):
    list_of_events=[]
    with open(filename, "r+") as file:
        data = file.read()
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

        if (line[0]=="") and (len(line)>1):
            header=line.copy()
            #first and last header column name is empty string, remove them.
            header.pop(0)
            header.pop(-1)
            i+=1
            line = re.sub(r"\$", "", data[i])
            line = re.sub(r"(\d+)\,(\d+)", r"\1\2", line)
            line = line.replace('"', '')
            line = line.split(',')
            #first and last column values are empty string
            line.pop(0)
            line.pop(-1)
            #list comprehension over slice iterate
            line[:] = [TryConvDate(x) for x in line]
            line[:] = [TryConvFloat(x) for x in line]
            #copy Date from last event to event_item header / value
            header.insert(0,"Date")
            line.insert(0,list_of_events[-1].event_dict['Date'])
            list_of_events[-1].add_item(header,line)
        else:
            try:
                #Fiscal event starts with a date.
                line[0] = datetime.strptime(line[0], '%m/%d/%Y')
                #print(f"{line[0]}")
                list_of_events.append(FiscalEvent(line))
            except ValueError as err:
                pass
        i = i+1
    return list_of_events

def TryConvDate(input: str):
    try:
        return datetime.strptime(input, '%m/%d/%Y')
    except ValueError as err:
        return input

def TryConvFloat(input: str):
    try:
        return float(input)
    except TypeError as err:
        return input
    except ValueError as err:
        return input

def ConvDate(input: pd.DataFrame):
    for name, values in input[['Purchase Date','Vest Date','Subscription Date']].items():
        if values != "":
            input[name] = datetime.strptime(values, '%m/%d/%Y')
        print(f"{input[name]}")
    return input
        #date = datetime.strptime(date, '%m/%d/%Y')
        #print(f'{date.day}.{date.month}.{date.year}')

def ConvDate(input: str):
    line=input.split()
    line[:]=[datetime.strptime(date, '%m/%d/%Y') for date in line]
    return line

def SaleEventsToPandas(obj_list: list[FiscalEvent], rates: NbpRatesDm1):
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
        fin_event.event_items_list[:] = [PurchaseDateRate(x, rates) for x in fin_event.event_items_list]
        sale_rate = rates.get_usd_pln_d_1(fin_event.event_dict['Date'])
        fin_event.event_items_list[:] = [AddSaleRate(x, sale_rate) for x in fin_event.event_items_list]
        fin_event.event_items_list[:] = [DropSurplusKeys(x) for x in fin_event.event_items_list]
        sale_df=pd.DataFrame.from_dict(fin_event.event_items_list)
        list_of_sale_df.append(sale_df)
 #       sale_df['purchase_rate_d-1']=sale_df.apply(lambda x: PurchaseDate(x, rates), axis=1)
        #print(event_df)

    return pd.concat(list_of_sale_df)

def AddSaleRate(sale_item: {}, sale_rate: float):
    sale_item['Sale Rate'] = sale_rate
    return sale_item

def PurchaseDateRate(sale_item: {}, rates: NbpRatesDm1):
    #ESPP and Div Reinvestment are purchased at Purchase Date
    #RS are vested at Vest Date
    if sale_item['Type']=="RS":
        sale_item['Purchase Date'] = sale_item['Vest Date']
        #RS are "bought" at zero price
        sale_item['Purchase Price'] = 0.00
    purchase_date = sale_item['Purchase Date']
    sale_item['Purchase Rate'] = rates.get_usd_pln_d_1(purchase_date)
    return sale_item

def DropSurplusKeys(sale_item: {}):
    sale_item.pop('Vest Date')
    sale_item.pop('Subscription Date')
    sale_item.pop('Subscription FMV')
    sale_item.pop('Purchase FMV')
    sale_item.pop('Disposition Type')
    sale_item.pop('Grant Id')
    sale_item.pop('Vest FMV')
    return sale_item


def PurchaseDate(sale_df: pd.DataFrame, rates: NbpRatesDm1):
    #ESPP and Div Reinvestment are purchased at Purchase Date
    if sale_df['Type']!="RS":
        return rates.get_usd_pln_d_1(sale_df['Purchase Date'])
    #RS are vested at Vest Date
    else:
        return rates.get_usd_pln_d_1(sale_df['Vest Date'])

def CalculateTax(items: pd.DataFrame, events: [], rates):
    items['Income']=items['Shares']*items['Sale Price']*items['Sale Rate']
    items['Cost']=items['Shares']*items['Purchase Price']*items['Purchase Rate']
    #print(f"{items['Cost'] }")
    income = items['Income'].sum()
    fees = 0.00
    for event in events:
        if event.event_dict["Action"] != "Sale":
            continue
#        print(f'Date: {event.event_dict["Date"]}, Fee: {float(event.event_dict["Fees"]) * rates.get_usd_pln_d_1(event.event_dict["Date"]) }')
        fees += float(event.event_dict['Fees'])* rates.get_usd_pln_d_1(event.event_dict["Date"])
    cost = items['Cost'].sum() + fees
    tax = (income - cost)*0.19
    print(f"income: {income}")
    print(f"cost: {cost}")
    print(f"Tax: {tax}")
# Press the green button in the gutter to run the script.
    


if __name__ == '__main__':
    # unittest.main()
    input="""
31.12.2019
10.06.2020
30.06.2020
31.12.2019
"""

    rates = NbpRatesDm1()
#    print(rates.get_usd_pln_d_1("26.01.2022"))
#    print(rates.get_usd_pln_d_1("27.04.2022"))
#    print(rates.get_usd_pln_d_1("27.07.2022"))
#    print(rates.get_usd_pln_d_1("26.10.2022"))

#    output=PurchaseDateRate({'Purchase Date': ConvDate("04/04/2022")[0],'Type':'ESPP'}, rates)
    input = parse_csv("/Users/mgrzesia/Documents/Dokumenty/PITy/Schwab/2022/fulll_EquityAwardsCenter_Transactions_20230325130430.csv")
    output = SaleEventsToPandas(input, rates)
    CalculateTax(output, input, rates)
    output=output.sort_values(by='Date')
    print(output[['Shares', 'Purchase Price', 'Purchase Rate', 'Cost']])

    input = parse_json("schwab-2022-mateusz.json")
    output = SaleEventsToPandas(input, rates)
    CalculateTax(output, input, rates)
    output=output.sort_values(by='Date')
    print(output[['Shares', 'Purchase Price', 'Purchase Rate', 'Cost']])


    #event = FiscalEvent('"08/18/2022", "Sale", "CSCO", "Share Sale", "139.9366", "$0.16", "Wire Transfer", "$6926.00"')
#    print(f"{rates.rates_cache}")
    #df = pd.read_csv(r'/Users/mgrzesia/Documents/Dokumenty/PITy/Schwab/2022/fulll_EquityAwardsCenter_Transactions_20230325130430.csv')
    #print(f"{df}")
#    print(f"input:\n{repr(input)}")
#    input.replace('\n',",")
#    print(type(input))
#    input=input.split()
#    print(input)
#    print(type(input))
    #for date in input:
        #print(get_usd_pln_d_1(date))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/




def ConvDate(input):
    line=input.split()
    for date in line:
        date = datetime.strptime(date, '%m/%d/%Y')
        print(f"{x.name}, {x}")
        print(f'{date.day}.{date.month}.{date.year}')




def GetRates(input):
    line = input.split()
    for date in line:
        datet = datetime.strptime(date, '%m/%d/%Y')
        date = str(datet.day)+"."+str(datet.month)+"."+str(datet.year)
        #print(f'{date}')
        rate = get_usd_pln_d_1(date,rates_cache)
        #print(f'{rate}')