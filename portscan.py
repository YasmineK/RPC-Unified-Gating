import os
import sys
import getopt
import errno
from subprocess import call
import xml.etree.ElementTree as ET

import loadConfParams



def run_scan(infile, xml_out_file):
    try:
        call(['nmap', '-iL', infile, '-p1-65535', 'P0', '-sV', '--version-all', '-oX', xml_out_file])
    except OSError(errno.ENOENT):     # No such file or directory error
        call(['apt-get', 'install', '-y', 'nmap'])


def parse_scan_results(infile, logfile):
    tree = ET.parse(infile)
    root = tree.getroot()

    # first ensure log file is not yet created
    if os.path.exists(logfile) is True:
        os.remove(logfile)

    log = open(logfile, 'a')


    for host in root.iter('host'):
        ip = host.find('address').get('addr')
        # print 'the host is ' + ip
        for port in host.find('ports').findall('port'):
            if port.find('state').get('state') == 'open':
                print 'found open ports'
                service = port.find('service')
                if service is not None:
                    service_name = service.get('name')
                    service_version = service.get('version')
                    if service_name is not None and service_version is not None:
                        print ip + ':' + port.get('portid') + ':' + service_name + ' - ' + service_version
                        log.write(ip + ':' + port.get('portid') + ':' + service_name + ' - ' + service_version + '\n')
                    elif service_name is not None:
                        print ip + ':' + port.get('portid') + ':' + service_name
                        log.write(ip + ':' + port.get('portid') + ':' + service_name + '\n')
                else:
                    print ip + ':' + port.get('portid')
                    log.write(ip + ':' + port.get('portid') + '\n')

    log.close()


def usage():
    print "Usage: portscan.py -i <inputFile> -o <outputFile>"


def main(argv):
    ip_file = ''
    result_file = ''

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', [])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    if len(opts) == 0:
        print 'You must pass an input file containing ip addresses.'
        usage()

    for option, arg in opts:
        if option == '-h':
            usage()
        elif option == '-i':
            ip_file = arg
        elif option == '-o':
            result_file = arg

    #if ip_file != '':
        #print 'Infile is ' + ip_file + '\n'

    config_params = loadConfParams.LoadConfParams()
    run_scan(ip_file, config_params.get_scan_xml_results())
    parse_scan_results(config_params.get_scan_xml_results(), result_file)


if __name__ == "__main__":
    main()
