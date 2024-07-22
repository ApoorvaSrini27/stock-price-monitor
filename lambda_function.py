import boto3
import requests
import json
import time
from botocore.exceptions import ClientError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Initialize clients
cloudwatch = boto3.client('cloudwatch')
appconfig = boto3.client('appconfig')
logs = boto3.client('logs')

LOG_GROUP_NAME = '/aws/lambda/StockPriceMonitor'

def get_stocks_list():
    try:
        response = appconfig.get_configuration(
            Application='StockMonitor',
            Environment='Production',
            Configuration='StocksList',
            ClientId='LambdaFunction'
        )
        stocks = json.loads(response['Content'].read())
        return stocks
    except ClientError as e:
        log_error(f"Error fetching AppConfig: {e}")
        return ['KAYNES', 'RELIANCE', 'TCS', 'INFY']  # Default list

def get_stock_price(symbol):
    base_url = "https://www.nseindia.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}",
    }
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(headers)
    try:
        session.get(base_url, headers=headers, timeout=10)
        time.sleep(2)  # Increased delay
        url = f"{base_url}/api/quote-equity?symbol={symbol}"
        response = session.get(url, headers=headers, timeout=15)  # Increased timeout
        if response.status_code == 200:
            data = response.json()
            return data['priceInfo']['lastPrice']
        else:
            log_error(f"Failed to fetch data for {symbol}. Status code: {response.status_code}")
            return None
    except Exception as e:
        log_error(f"Error fetching stock price for {symbol}: {e}")
        return None
        
def emit_metric(symbol, price):
    cloudwatch.put_metric_data(
        Namespace='StockPrices',
        MetricData=[
            {
                'MetricName': 'StockPrice',
                'Dimensions': [
                    {   
                        'Name': 'Symbol',
                        'Value': symbol
                    },
                ],
                'Value': price,
                'Unit': 'None'
            },
        ]
    )

def log_error(message):
    logs.put_log_events(
        logGroupName=LOG_GROUP_NAME,
        logStreamName='errors',
        logEvents=[
            {   
                'timestamp': int(time.time() * 1000),
                'message': message
            },
        ]
    )       

def lambda_handler(event, context):
    stocks = get_stocks_list()
    for symbol in stocks:
        price = get_stock_price(symbol)
        if price is not None:
            emit_metric(symbol, price)
            print(f"Emitted metric for {symbol}: {price}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Metrics emitted successfully')
    }                   
