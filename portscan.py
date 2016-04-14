import getopt
import sys
import os
from subprocess import call
import xml.etree.ElementTree as ET


def run_scan(infile):
    call(['nmap', '-iL', infile, '-p1-65535', '-oX', 'xml_results.xml'])

def parse_scan_results(infile, logfile, port_list):
    tree = ET.parse(infile)
    root = tree.getroot()
    open_ports = []

    for host in root.iter('host'):
        ip = host.find('address').get('addr')
        #print 'the host is ' + ip
        for port in host.find('ports').findall('port'):
            #print 'found all ports'
            if port.find('state').get('state') == 'open':
                print 'found open ports'
                open_ports.append(ip + ':' + port.get('portid'))

        # Now look for specific ports and print them
        # first ensure log file is not yet created
        if os.path.exists(logfile) is True:
            os.remove(logfile)

        log = open(logfile, 'a')

        for i in range(0, len(open_ports)):
            if str(open_ports[i]).split(':')[1] in port_list:
                # log_file.append(port + '\n')
                print str(open_ports[i])
                log.write(open_ports[i] + '\n')

        log.close()


    def usage():
        print "portscan.py -i <inputFile> -o<outputFile>"

def main(argv):
    port_list = ['22','80','443','514','3306','4369','5000','5672','5900',
                 '6080','6081','8040','8090','8773','8774','8775','8776',
                 '8777','9191','9292','9696','11211','15672','16509','35357',
                 '37673','38150','42020','44205','55672','56285']
    inFile = ''
    outFile = ''

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', [])
    except getopt.GetoptError as err:
        print str(err)
        # usage()
        sys.exit(2)

    for option, arg in opts:
        if option == '-h':
            print 'usage: portscan.py -i <inputFile> -o <outputFile>'
        elif option == '-i':
            inFile = arg
        elif option == '-o':
            outFile = arg

    if inFile != '':
        print 'Infile is ' + inFile + '\n'
        run_scan(inFile)
        parse_scan_results('xml_results.xml', 'portscanlog.txt', port_list)

if __name__ == "__main__":
    main(sys.argv[1:])