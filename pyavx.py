'''
Class to connect to the Aviatrix Controller and run some APIs.
'''

import os, requests

class Pyavx:
  def api_call(self, data, version='v1'):
    '''
    Post Aviatrix API with version specified, run the specified cmd.
    '''
    if version not in ['v1', 'v2']:
      print('API version must be v1 or v2.')
      return None

    if not data:
      print('GET/POST must have data.')
      return None

    if not self.cid and data['action'] not in ['login', 'get_api_token']:
      print('CID needed for this to work.')
      return None

    data['CID'] = self.cid
   
    url = f'https://{self.ip}/{version}/api'
    self.r = requests.post(url, headers=self.headers, data=data, verify=False)
    return self.r.json()

  def __init__(self):
    '''
    Username/pw/controller ip in environment just like terraform.
    
    $ export AVIATRIX_CONTROLLER_IP="1.2.3.4"
    $ export AVIATRIX_USERNAME="admin"
    $ export AVIATRIX_PASSWORD="password"

    PS> Set-Item -Path Env:AVIATRIX_CONTROLLER_IP -Value '1.2.3.4'
    PS> Set-Item -Path Env:AVIATRIX_USERNAME -Value 'admin'
    PS> Set-Item -Path Env:AVIATRIX_PASSWORD -Value 'password'
    '''

    requests.packages.urllib3.disable_warnings() 
    self.ip = os.getenv('AVIATRIX_CONTROLLER_IP')
    u = os.getenv('AVIATRIX_USERNAME')
    p = os.getenv('AVIATRIX_PASSWORD')

    self.cid = None
    self.headers = None

    #Get API token.
    data = {
      'action': 'get_api_token'
    }
    r = self.api_call(data, version='v2')

    if r['return'] and type(r['results'] == dict):
      self.headers = {'X-Access-Key': r['results']['api_token']}
    else:
      print(f'Error getting api_token. {r["reason"]}')
      exit()

    if self.headers:
      print('API token received.')
    else:
      print('Error getting API token.')
      exit()

    # Get the CID
    data = {
      'action': 'login',
      'username' : u,
      'password' : p
    }

    r = self.api_call(data, version='v2')

    if r['return']:
      self.cid = r.get('CID')
    else:
      print(f'Error getting CID. {r["reason"]}')
      exit()

    if self.cid:
      print("CID received.")
    else:
      print(f"Error with CID.")
      exit()