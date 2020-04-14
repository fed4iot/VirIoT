from eve import Eve

def remove_secret_fields(resource, response):
    del(response['_etag'])
    #del(response['_created'])
    del(response['_updated'])
    # remove @context if it exists
    response.pop("@context", None)
    del(response['_id'])

def remove_secret_fields_in_list(resource, response):
    for item in response['_items']:
        remove_secret_fields(resource, item)


app = Eve()
app.on_fetched_item += remove_secret_fields
app.on_fetched_resource += remove_secret_fields_in_list


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
