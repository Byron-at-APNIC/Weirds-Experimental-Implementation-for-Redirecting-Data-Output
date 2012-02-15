from django.http import HttpResponse
from django.utils import simplejson
from django.utils.datastructures import SortedDict

import socket

def lookup(query, host='org.whois-servers.net', port=43):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(query + "\r\n")
    response = ''
    while True:
        d = s.recv(4096)
        if not d:
            break
        response += d
    s.close()
    return parse(response)

def parse(response):
    # For org, take the first paragraph as a T&C entry
    response = response.replace('\r\n', '\n')
    (terms, record) = response.split('\n\n', 1)
    lines = [[i.strip() for i in _.strip().split(':', 1)]
            for _ in record.split('\n') if _.strip() != '']
    return {'terms': terms, 'record': lines}

def camelCase(datum):
    if isinstance(datum, list):
        return [camelCase(item) for item in datum]
    else:
        camel = datum.title().replace(' ', '')
        return camel[:1].lower() + camel[1:]

def dateFormat(datum):
    months = {'Jan': '01', 'Feb': '02', 'Mar': '03',
              'Apr': '04', 'May': '05', 'Jun': '06',
              'Jul': '07', 'Aug': '08', 'Sep': '09',
              'Oct': '10', 'Nov': '11', 'Dec': '12'}
    if isinstance(datum, list):
        return [dateFormat(item) for item in datum]
    else:
        # 20-Dec-2008 03:56:33 UTC
        return datum[7:11] + "-" + months[datum[3:6]] + \
            datum[0:2] + 'T' + datum[12:20] + 'Z'

def makeEntity(prefix, data):
    entity = SortedDict()
    entity['handle'] = data[prefix + ' ID']
    entity['names'] = [data[prefix + ' Name']]
    entity['postalAddress'] = [
            data[prefix + ' Street1'],
            data[prefix + ' Street2'],
            data[prefix + ' Street3'],
            data[prefix + ' City'],
            data[prefix + ' State/Province'],
            data[prefix + ' Postal Code'],
            data[prefix + ' Country'],
    ]
    entity['emails'] = [data[prefix + ' Email']]
    entity['phones'] = {
        'office': [data[prefix + ' Phone']],
        'fax': [data[prefix + ' FAX']],
        'mobile': []
    }
    entity['registrationDate'] = dateFormat(data['Created On'])

    return entity

def name(request, domain):
    data = lookup(domain)

    # Convert data to a dictionary
    datadict = {'terms': data['terms']}
    for pairs in data['record']:
        if pairs[0] in datadict:
            if isinstance(datadict[pairs[0]], list):
                datadict[pairs[0]].append(pairs[1])
            else:
                datadict[pairs[0]] = [datadict[pairs[0]], pairs[1]]
        else:
            datadict[pairs[0]] = pairs[1]

    response = SortedDict()
    response['domain'] = SortedDict()
    response['domain']['handle'] = datadict['Domain ID']
    response['domain']['name'] = datadict['Domain Name']
    response['domain']['status'] = camelCase(datadict['Status'])
    response['domain']['registrationDate'] = dateFormat(datadict['Created On'])
    response['domain']['expirationDate'] = dateFormat(datadict['Expiration Date'])
    response['domain']['remarks'] = datadict['terms'].split('\n')
    response['domain']['nameServers'] = [ns for ns in datadict['Name Server'] if ns != '']
    # todo: delegationKeys

    response['registrant'] = SortedDict()
    response['registrant']['entity'] = makeEntity('Registrant', datadict)
    response['registrant']['contacts'] = SortedDict()
    response['registrant']['contacts']['tech'] = makeEntity('Tech', datadict)
    response['registrant']['contacts']['admin'] = makeEntity('Admin', datadict)


    output = simplejson.dumps(response, indent='  ')

    return HttpResponse(output, mimetype="application/json")

if __name__ == '__main__':
    print name(None, 'iana.org')
