Run manually using UV:

1. Download the code - Code -> Download Zip

2. Unzip

3. Open shell and install UV:
```
pip install uv
```
4. Create venv using UV:
```
uv sync
```
5. Run the script:
```
uv run mainjson.py tests/2023_test.json output.xlsx

     Type   Shares        PurchaseDate  PurchasePrice USD  PurchaseUSDRate D-1 PLN   SaleDate  SalePrice USD  GrossProceeds USD  Amount USD  FeesAndCommissions USD  SaleUSDRate D-1 PLN  PurchaseCost PLN  FeesAndCommissions PLN  GrossProceeds PLN  TotalCost PLN  Tax PLN
     ESPP   0.8082 2022-06-30 00:00:00            36.2440                   4.4533 2023-10-17        53.4208              43.17        0.00                    0.00               4.2505            130.45                    0.00             183.51            NaN      NaN
     ESPP   7.1697 2022-06-30 00:00:00            36.2440                   4.4533 2023-10-17        53.4208             383.01        0.00                    0.00               4.2505           1157.23                    0.00            1627.99            NaN      NaN
Div Reinv   3.7330 2022-10-28 00:00:00            44.9465                   4.7216 2023-10-17        53.4208             199.42        0.00                    0.00               4.2505            792.21                    0.00             847.63            NaN      NaN
     ESPP 570.8443 2022-12-30 00:00:00            36.2100                   4.4078 2023-10-17        53.4208           30494.96        0.00                    0.00               4.2505          91110.43                    0.00          129618.82            NaN      NaN
     Sale 582.5552                                 0.0000                   0.0000 2023-10-17         0.0000               0.00    31120.56                    0.05               4.2505              0.00                    0.21               0.00            NaN      NaN
      NaN      NaN                 NaN                NaN                      NaN        NaT            NaN                NaN         NaN                     NaN                  NaN          93190.32                    0.21          132277.96       93190.53  7426.61

      DividendDate  Income USD  TaxWitholded USD  DividendUSDRate D-1 PLN  Income PLN  TaxPL PLN  TaxWitholdedInUS PLN  TaxDue PLN
        2023-10-25       418.0              62.7                   4.1884     1750.75     332.64                262.61         NaN
Total          NaT         NaN               NaN                      NaN     1750.75     332.64                262.61       70.03

Excel file 'output.xlsx' saved successfully.
```


Run manually using venv:

 Creation of venv
  #install python version you wish to run in venv:
```  
brew install python@3.11
rehash
```
#Create venv, choose the folder. In my case ~/espp.
#could be e.g. ~/python-projects/espp/venv
#venv name is espp - it is the name of the folder
```
mkdir ./venv
python3.11 -m venv ./venv --clear --prompt='espp@3.11'
```
#Activate the venv
```
source venv/bin/activate
```
#Install modules
```
pip install -U pip requests pandas xlsxwriter certifi aiohttp
```
#Run the script
```
python3 main-json.py input_data.json output.xlsx
``` 
