#acpi: access control policy ID
#ae_rn: resouce name of the AE
#container_rn: resource name of the container, e.g. 
#CSEurl: url of the CSE server
#lbl: labels array
#rn : resource name
#ri : resource identifier
#mni: max num instances
#nu: norification uri (url or AE ri if AE containd poa)
#origin: originator identifier (AE ri usually)
#poa: point of access, url where to be contacted (rr=true)
#rr: true/false if should be reachable (request reachability)
#sub_rn: sub resource name



import requests
import json


def cb_query(user, CSEurl,rcn):
    querystring = {"rcn":rcn}

    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': user,
        'cache-control': "no-cache",
        }
    response = requests.request("GET", CSEurl, headers=headers, params=querystring)
    return response.text



#Create AE
def ae_create (ae_rn,origin,api,rr,poa,lbl,CSEurl):
    querystring = {"rcn":"3"}
    url = CSEurl+"/Mobius"
    ae_value ={}
    ae_value['rn']=ae_rn
    ae_value['lbl']=lbl
    ae_value['api']=api
    ae_value['rr']=rr
    data = {}
    data['m2m:ae'] = ae_value
    
    if (rr==True):
        ae_value['poa']=poa
    payload = json.dumps(data)
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': origin,
        'content-type': "application/vnd.onem2m-res+json;ty=2",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    ae=response.json()
    if (response.status_code==201):
        res=response.json()
        uri=res['m2m:rce']['uri']
        ae=res['m2m:rce']['m2m:ae']
        ae['uri']=uri
    return(response.status_code,ae)



#Delete AE
def ae_delete (ae_uri,origin,CSEurl):
    url = CSEurl+"/"+ae_uri
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': origin,
        'cache-control': "no-cache",
        }
    response = requests.request("DELETE", url, headers=headers)
    res=response.json()
    if (response.status_code==200):
        res=res['m2m:ae']
    return(response.status_code,res)



#Create container
def container_create(container_rn,origin,ae_uri,mni,lbl,CSEurl):
    querystring = {"rcn":"3"}   
    url = CSEurl+"/"+ae_uri
    cnt_value ={}
    cnt_value['rn']=container_rn
    cnt_value['lbl']=lbl
    cnt_value['mni']=mni
    data = {}
    data['m2m:cnt'] = cnt_value
    payload = json.dumps(data)
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': origin,
        'content-type': "application/vnd.onem2m-res+json; ty=3",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers,params=querystring)
    cnt=response.json()
    if (response.status_code==201):
        res=response.json()
        uri=res['m2m:rce']['uri']
        cnt=res['m2m:rce']['m2m:cnt']
        cnt['uri']=uri
    return(response.status_code,cnt)
    
    
    
#Delete container    
def container_delete(container_uri,origin,CSEurl):
    url = CSEurl+"/"+container_uri
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': origin,
        'cache-control': "no-cache",
        }
    response = requests.request("DELETE", url, headers=headers)
    res=response.json()
    if (response.status_code==200):
        res=res['m2m:cnt']
    return(response.status_code,res)


#Get container
def container_get(container_uri,origin,CSEurl):
    url = CSEurl+"/"+container_uri
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",    #not necessary
        'x-m2m-origin': origin,
        'cache-control': "no-cache",
    }
    response=requests.request("GET", url, headers=headers)
    #print(response.json())
    cnt=response.json()
    return(response.status_code,cnt)

#Create cin
def create_cin(container_uri,origin,value,CSEurl):
    querystring = {"rcn":"3"}    
    url = CSEurl+"/"+container_uri
    data_con = {}
    data_con['con']=value
    data={}
    data['m2m:cin'] = data_con
    payload = json.dumps(data)
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345", #not usefull
        'x-m2m-origin': origin,
        'content-type': "application/vnd.onem2m-res+json; ty=4",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers,params=querystring)
    cin=response.json()
    if (response.status_code==201):
        res=response.json()
        uri=res['m2m:rce']['uri']
        cin=res['m2m:rce']['m2m:cin']
        cin['uri']=uri
        #print(res)
    return(response.status_code,cin)



#Get cin
def get_cin_latest(container_uri,origin,CSEurl):
    url = CSEurl+"/"+container_uri+"/la"
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",    #not necessary
        'x-m2m-origin': origin,
        'cache-control': "no-cache",
    }
    response=requests.request("GET", url, headers=headers)
    print(response.json())
    cin=response.json()
    return(response.status_code,cin)



#Create subscrtion
def sub_create(sub_rn,origin,nu,container_uri,CSEurl):
    querystring = {"rcn":"3"}   
    url = CSEurl+"/"+container_uri
    enc_value={}
    enc_value['net']=[3]
    sub_value ={}
    sub_value['rn']=sub_rn
    sub_value['nu']=nu
    sub_value['nct']=2
    sub_value['pn']=2
    sub_value['enc']=enc_value
    data = {}
    data['m2m:sub'] = sub_value
    payload = json.dumps(data)
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': origin,
        'content-type': "application/vnd.onem2m-res+json; ty=23",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    sub=response.json()
    if (response.status_code==201):
        res=response.json()
        uri=res['m2m:rce']['uri']
        sub=res['m2m:rce']['m2m:sub']
        sub['uri']=uri
        #print(res)
    return(response.status_code,sub)



#Delete subscrtion
def sub_delete(sub_uri,origin,CSEurl):
    url = CSEurl+"/"+sub_uri
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'x-m2m-origin': origin,
        'cache-control': "no-cache",
        }
    response = requests.request("DELETE", url, headers=headers)
    res=response.json()
    if (response.status_code==200):
        res=res['m2m:sub']
    return(response.status_code,res)



#if in the container is present a policy, the ae would have access denied
#note: the policy name can also be a not-real name

#Create access control policy
def acp_create(CSEurl, origin, rn_acp, pv, pvs):
    acp={"m2m:acp":{"rn": rn_acp,"pv":pv,"pvs":pvs}}
    url = CSEurl+"/Mobius"
    headers = {
        'x-m2m-ri': "12345",
        'content-type': "application/vnd.onem2m-res+json; ty=1",
        'accept': "application/json",
        'x-m2m-origin': origin,
        'cache-control': "no-cache"
        }
    response = requests.request("POST", url, data=json.dumps(acp) , headers=headers)
    res=response.json()
    if (response.status_code==201):
        res=res['m2m:acp']
    return(response.status_code,res)



#Delete access control policy
def acp_delete(CSEurl, origin, acp_rn):
    url = CSEurl+"/Mobius/"+acp_rn
    headers = {
        'x-m2m-ri': "12345",
        'accept': "application/json",
        'x-m2m-origin': origin,
        }
    response = requests.request("DELETE", url, headers=headers)
    res=response.json()
    if (response.status_code==200):
        res=res['m2m:acp']
    return(response.status_code,res)



#Insert access control policy in an ae
def ae_acp_update(CSEurl, origin, ae_rn, acpi):
    sub_value = {}
    sub_value['acpi'] = [1]
    sub_value['acpi'][0] = acpi 
    data = {}
    data['m2m:ae'] = sub_value
    payload = json.dumps(data)
    url = CSEurl+"/Mobius/"+ae_rn
    headers = {
        'accept': "application/json",
        'x-m2m-ri': "12345",
        'content-type': "application/vnd.onem2m-res+json",
        'x-m2m-origin': origin,
        'cache-control': "no-cache"
        }
    response = requests.request("PUT", url, data=payload, headers=headers)
    res=response.json()
    if (response.status_code==200):
        res=res['m2m:ae']
    return(response.status_code,res)


#Insert access control policy in an container
def ae_cnt_acp_update(CSEurl, origin, ae_rn, ae_cnt_rn, acpi):
    return(ae_acp_update(CSEurl, origin, ae_rn+"/"+ae_cnt_rn, acpi))
