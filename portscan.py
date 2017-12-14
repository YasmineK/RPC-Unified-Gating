import os
import argparse
import errno
import xml.etree.ElementTree as ET

from subprocess import call
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from scp import SCPClient

import loadConfParams as lcp


''' Downloads the inventory file from the deployment host '''


def download_inventory_list(deployment_host, path_to_inventory, uname):
    with SSHClient() as ssh_client:
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(deployment_host, username=uname)
        scp = SCPClient(ssh_client.get_transport())
        scp.get(path_to_inventory)


''' Runs Nmap '''


def run_scan(infile, xml_out_file):
    try:
        call(['nmap', '-iL', infile, '-p1-65535', 'P0', '-sV', '--version-all', '-oX', xml_out_file])
    except OSError(errno.ENOENT):     # No such file or directory error
        call(['apt-get', 'install', '-y', 'nmap'])
        run_scan(infile, xml_out_file)


''' Parses Nmap XML results and logs open services '''


def parse_scan_results(infile, logfile):
    tree = ET.parse(infile)
    root = tree.getroot()

    # first ensure existing log file is removed
    if os.path.exists(logfile):
        os.remove(logfile)

    with open(logfile, 'a') as log:
        for host in root.iter('host'):
            ip = host.find('address').get('addr')
            for port in host.find('ports').findall('port'):
                if port.find('state').get('state') == 'open':
                    print 'found open ports'
                    service = port.find('service')
                    if service is not None:
                        service_name = service.get('name')
                        service_version = service.get('version')
                        if service_name is not None and service_version is not None:
                            output = "{ip} : \t {portID} : \t {sevice_name} - \t {service_version}".format(
                                ip=ip, portID=port.get('portid'), service_name=service_name,
                                service_version=service_version)
                            print output
                            log.write(output + '\n')
                        elif service_name is not None:
                            output = "{ip} : \t {portID} : \t {service_name}".format(
                                ip=ip, portID=port.get('portid'), service_name=service_name)
                            print output
                            log.write(output + '\n')
                    else:
                        output = "{ip} : \t {portID}".format(ip=ip,  portID=port.get('portid'))
                        print output
                        log.write(output + '\n')


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('deploy_host_ip', help='The IP of the deployment host')
    args = parser.parse_args()

    config_params = lcp.LoadConfParams()
    # download the inventory list locally
    download_inventory_list(args.deploy_host_ip, config_params.hostnames_path, 'root')

    run_scan(config_params.get_local_ip_list(), config_params.scan_xml_results)
    parse_scan_results(config_params.scan_xml_results, config_params.scan_final_results)


if __name__ == "__main__":
    main()
