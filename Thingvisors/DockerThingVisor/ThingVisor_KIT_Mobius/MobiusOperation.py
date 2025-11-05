# 参考：https://www.ttc.or.jp/application/files/9815/5306/4184/3-1R_oneM2M20180831.pdf
#      https://www.ttc.or.jp/application/files/6715/5306/4187/3-2R_oneM2M20180831_program.pdf

import requests


def response_check(response: requests.Response):
    print(response.url, response)
    try:
        print(response.text)
    except:
        pass

    # response.raise_for_status()

    return response


def ae_create(mobius_url, api_name, resource_name, rr = False, X_M2M_Origin = 'S', X_M2M_RI = '1'):
    headers = {
        'Content-Type':'application/json;ty=2', 
        'X-M2M-Origin': X_M2M_Origin, 
        'X-M2M-RI': X_M2M_RI
    }
    body = {
        'm2m:ae': {
            'api' : api_name,
            'rn' : resource_name,
            'rr' : rr
        }
    }
    return response_check(requests.post(mobius_url, json=body,headers=headers))


def ae_get(mobius_url, resource_name, X_M2M_Origin = '', X_M2M_RI = '2'):
    headers = {
        'Content-Type':'application/json;ty=2', 
        'X-M2M-Origin': X_M2M_Origin, 
        'X-M2M-RI': X_M2M_RI
    }
    return response_check(requests.get(mobius_url + '/' +
resource_name,headers=headers))


def container_create(mobius_url, resource_name, sensor_name, ae_id, X_M2M_RI = '2'):
    headers = {
        'Content-Type':'application/json;ty=3', 
        'X-M2M-Origin': ae_id,
        'X-M2M-RI': X_M2M_RI
    }
    body = {
        'm2m:cnt': {
            'rn' : sensor_name
        }
    }
    return response_check(requests.post(mobius_url + r'/' + resource_name, json=body, headers=headers))


def subscription_create(mobius_url, resource_name, sensor_name, ae_id, subscription_url: list, X_M2M_RI = '3'):
    headers = {
        'Content-Type':'application/json;ty=23', 
        'X-M2M-Origin': ae_id,
        'X-M2M-RI': X_M2M_RI
    }
    body = {
        'm2m:sub': {
            'enc': {
                'net': [
                    3
                ]
            },
            'ln': True,
            'nu': subscription_url,
            'nct': 1,
            'rn': sensor_name + '_subscription'
        }
    }
    return response_check(requests.post(mobius_url + r'/' + resource_name + r'/' + sensor_name, json=body, headers=headers))


def content_instance_create(mobius_url, resource_name, sensor_name, ae_id, content_info, content, X_M2M_RI = '4'):
    headers = {
        'Content-Type':'application/json;ty=4', 
        'X-M2M-Origin': ae_id,
        'X-M2M-RI': X_M2M_RI
    }
    body = {
        'm2m:cin': {
            'cnf' : content_info,
            'con' : content
        }
    }
    return response_check(requests.post(mobius_url + r'/' + resource_name + r'/' + sensor_name, json=body, headers=headers))


def retrieve(mobius_url, resource_name, ae_id, X_M2M_RI = '5'):
    headers = {
        'Content-Type':'application/json',
        'X-M2M-Origin':ae_id,
        'X-M2M-RI': X_M2M_RI
    }
    return response_check(requests.get(mobius_url + r'/' + resource_name, headers=headers))


def discovery(mobius_url, resource_name, ae_id, X_M2M_RI = '6'):
    headers = {
        'Content-Type':'application/json',
        'X-M2M-Origin':ae_id,
        'X-M2M-RI': X_M2M_RI,
    }
    params = {
        'fu':'1'
    }
    return response_check(requests.get(mobius_url + r'/' + resource_name, headers=headers, params=params))


def ae_delete(mobius_url, resource_name, ae_id, X_M2M_RI = '8'):
    headers = {
        'Content-Type':'application/json;ty=2', 
        'X-M2M-Origin': ae_id, 
        'X-M2M-RI': X_M2M_RI
    }
    return response_check(requests.delete(mobius_url + r'/' + resource_name, headers=headers))


def get_sensor_data(mobius_url, resource_name, sensor_name, ae_id, X_M2M_RI = '8', is_latest = True):
    headers = {
        'Content-Type':'application/json',
        'X-M2M-Origin':ae_id,
        'X-M2M-RI': X_M2M_RI,
    }
    url = mobius_url + '/' + resource_name + '/' + sensor_name
    if is_latest:
        url += '/la'
    return response_check(requests.get(url, headers=headers))

