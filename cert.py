from subprocess import call
import xml.etree.ElementTree as ET


# Run SSLyze on all URLs included in a file

def sslyze_cert(inFile):
    URLs = open(inFile, "r")

    counter = 0
    for uri in URLs:
        print uri + '\n'
        counter += 1
        call(['python', '/Users/yasm8029/mytools/sslyze/sslyze.py', '--regular',
               '--xml_out=ssl_results_' + str(counter) + '.xml',  uri.rstrip()+':443'])

    URLs.close()
    return counter

# Parses XML output of sslyze command and writes issues to a log file
# Checks for the following:
#  - Cert validity and public key
#  - Compression
#  - heartbleed
#  - ciphers and key sizes, MAC, SSL versions, renegotiation
def parse_xml_results(counter):
    for x in range(1, counter + 1):
        file = open('ssl_results_' + str(x), 'a')
        tree = ET.parse('ssl_results_' + str(x) + '.xml')
        root = tree.getroot()

        # check key size
        for pk_size in root.iter('publicKeySize'):
            if pk_size.text.split()[0] < 1024:
                file.write('Weak Public Key Size \n')
                break
        # check TLS compression
        for compression in root.iter('compressionMethod'):
            if compression.attrib["isSupported"] == "True":
                file.write('Compression Supported \n')
                break
        # check for heartbleed vuln.
        for heartbleed in root.iter('heartbleed'):
            hb = heartbleed.find('heartbleed')
            if hb is not None:
                # print 'inside loop'
                if hb.get('isVulnerable') == 'True':
                    file.write('Server is Vulnerable to Heartbleed \n')
                    break

        # check for client renegociation
        for reneg in root.iter('sessionRenegotiation'):
            if reneg.attrib['canBeClientInitiated'] == 'True':
                file.write('Client Renegotiation Supported \n')
            if reneg.attrib['isSecure'] == 'False':
                file.write('Renegotiation is Not Secure \n')

        for ssl2 in root.iter('sslv2'):
            if ssl2.find('acceptedCipherSuites').find('cipherSuite') is not None:
                file.write('SSL2 Supported \n')

        # check for POODLE
        for ssl3 in root.iter('sslv3'):
            if ssl3.find('acceptedCipherSuites').find('cipherSuite') is not None:
                file.write('SSL3 Supported \n')

        # the following three outer loops check for weak ciphers/digests in accepted protocols
        for tls1 in root.iter('tlsv1'):
            acceptedCipherSuites = tls1.find('acceptedCipherSuites')
            for cipher in acceptedCipherSuites.iter('cipherSuite'):
                #print cipher.get('keySize')
                if cipher.get('anonymous') == 'True':
                    file.write('TLS1 Accepts Anonymous Cipher Suites \n')
                if int(cipher.get('keySize')) < 128:
                    file.write('TLS1 Has Weak Encryption Key Size \n')
                if 'RC4' in cipher.get('name'):
                    file.write('TLS1 Supports RC4 \n')
                if 'MD5' in cipher.get('name'):
                    file.write('TLS1 Supports MD5 \n')

        for tls1_1 in root.iter('tlsv1_1'):
            acceptedCipherSuites = tls1_1.find('acceptedCipherSuites')
            #print acceptedCipherSuites
            for cipher in acceptedCipherSuites.iter('cipherSuite'):
                if cipher.get('anonymous') == 'True':
                    file.write('TLS1_1 Accepts Anonymous Cipher Suites \n')
                if int(cipher.get('keySize')) < 128:
                    file.write('TLS1_1 Has Weak Encryption Key Size \n')
                if 'RC4' in cipher.get('name'):
                    file.write('TLS1_1 Supports RC4 \n')
                if 'MD5' in cipher.get('name'):
                    file.write('TLS1_1 Supports MD5 \n')

        for tls1_2 in root.iter('tlsv1_2'):
            acceptedCipherSuites = tls1_2.find('acceptedCipherSuites')
            #print acceptedCipherSuites
            for cipher in acceptedCipherSuites.iter('cipherSuite'):
                if cipher.get('anonymous') == 'True':
                    file.write('TLS1_2 Accepts Anonymous Cipher Suites \n')
                if int(cipher.get('keySize')) < 128:
                    file.write('TLS1_2 Has Weak Encryption Key Size \n')
                if 'RC4' in cipher.get('name'):
                    file.write('TLS1_2 Supports RC4 \n')
                if 'MD5' in cipher.get('name'):
                    file.write('TLS1_2 Supports MD5 \n')

        x += 1

    file.close()

def main():
    '''counter = sslyze_cert('url')
    print counter'''

    parse_xml_results(sslyze_cert('url'))

    #parse_xml_results(1)

if __name__ == "__main__":
    main()




