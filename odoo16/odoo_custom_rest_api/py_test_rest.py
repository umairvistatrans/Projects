"""
--Options--
query={-image_1920,-image_1024,-image_256,-image_128,-image_512} or query {id,name}
filter=[["id", ">", 60]]
page_size=5
page=5
limit=5
api/product.template/record_id/?query...
"""
import requests, json
from pprint import pprint

payload = {"jsonrpc": "2.0", "params":  {
        "login": "admin",
        "password": "1",
        "db": "7md_ae"
    }}

post_request=requests.post('http://localhost:8012/auth/',data=json.dumps(payload),headers={'content-type': 'application/json'}).json()
cookies_dict = {"session_id": post_request['result']['session_id']}
product_template_request=requests.get('http://localhost:8012/api/product.template/?query={-image_1920,-image_1024,-image_256,-image_128,-image_512}&limit=10',cookies=cookies_dict)
pprint(product_template_request.json())
product_variant_request=requests.get('http://localhost:8012/api/product.product/461/',cookies=cookies_dict)
pprint(product_variant_request.json())
product_category_request=requests.get('http://localhost:8012/api/product.category/?limit=10',cookies=cookies_dict)
pprint(product_category_request.json())
product_brand_request_request=requests.get('http://localhost:8012/api/product.brand/',cookies=cookies_dict)
pprint(product_brand_request_request.json())
customer_request=requests.get('http://localhost:8012/api/res.partner/?limit=3',cookies=cookies_dict)
pprint(customer_request.json())