'''
Enables SNAT/DNAT and creates a lot of DNAT rules.
'''

import pyavx
import argparse, json
from ipaddress import IPv4Address, IPv4Network

DEFAULT_SNAT_IP = '192.168.31.4'
DEFAULT_DNAT_POOL = '172.31.0.0/16'
DEFAULT_DPORT_START = 5000

def enable_snat(gw, snat_ip, dnat_pool, dst_interface):
  policy_list = [
    {
      'dst_ip': dnat_pool,
      'protocol': 'all',
      'connection': f'{dst_interface}@site2cloud',
      'mark': '75000',
      'new_src_ip': snat_ip,
      'apply_route_entry': False
    }
  ]

  data = {
    'action': 'enable_snat',
    'gateway_name': gw,
    'mode': 'custom',
    'policy_list': []
  }

  if pyavx.api_call({'action': 'get_gateway_snat_config', 'gateway_name': gw})['results']['snat_config'] != '[]': 
    #Disable custom SNAT
    r = pyavx.api_call(data)

    if not r['return']:
      print(f'Disable gateway {gw} custom SNAT failed.')
      print(r['reason'])
      exit()

  data['policy_list'] = json.dumps(policy_list)
  
  r = pyavx.api_call(data)

  if r['return']:
    print(f'Set gateway {gw} SNAT to {snat_ip}. ')
    return
  else:
    print(f'Setting gateway {gw} SNAT to {snat_ip} failed.')
    print(r['reason'])
    exit()

def enable_dnat(gw, count, dnat_pool, dnat_port_start, snat_ip, src_interface):
  policy_list = []
  dnat_pool_network = IPv4Network(dnat_pool)
   # Generate rules
  for i in range(count):
    policy = {
      'dst_ip': f'{snat_ip}/32',
      'dst_port': str(dnat_port_start + i),
      'protocol':'tcp',
      'connection': f'{src_interface}@site2cloud',
      'mark':'75000',
      'new_dst_ip': str(dnat_pool_network[i]),
      'new_dst_port':'443'
    }

    policy_list.append(policy)
  
  data = {
    'action': 'update_dnat_config',
    'gateway_name': gw,
    'policy_list': json.dumps(policy_list)
  }

  r = pyavx.api_call(data, version='v2')
  if r['return']:
    print(f'Set gateway {gw} DNAT with {count} entries.')
    return
  else:
    print(f'Setting gateway {gw} DNAT with {count} entries failed.')
    print(r['reason'])
    exit()



###################
# Main
###################

# Command line arguments
flags = argparse.ArgumentParser(description = 'NAT test on Aviatrix.')
flags.add_argument('--count', '-c', dest='count', action='store', required=True, help='Number of NAT entries.', type=int)
flags.add_argument('--gwname', '-g', dest='gw', action='store', required=True, help='Gateway name')
flags.add_argument('--srcint', '-i', dest='srcint', action='store', required=True, help='Gateway source interface')
flags.add_argument('--dstint', '-o', dest='dstint', action='store', required=True, help='Gateway destination interface')
flags.add_argument('--snatip', '-s', dest='snat_ip', action='store', required=False, help='Source NAT IP.', default=DEFAULT_SNAT_IP)

flags.add_argument('--dnatpool', '-d', dest='dnat_pool', action='store', required=False, help='DNAT POOL', default=DEFAULT_DNAT_POOL)
flags.add_argument('--dnatportstart', '-p', dest='dnat_port', action='store', required=False, help='Starting DNAT port.', default=DEFAULT_DPORT_START, type=int)
args = flags.parse_args()

pyavx = pyavx.Pyavx()

if not pyavx:
  print('Check your environment variables.')
  exit()

enable_snat(args.gw, args.snat_ip, args.dnat_pool, args.dstint)
enable_dnat(args.gw, args.count, args.dnat_pool, args.dnat_port, args.snat_ip, args.srcint)