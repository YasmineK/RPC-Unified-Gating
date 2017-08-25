import os
import logging
from subprocess import call

try:
    import yaml
except ImportError:
    call(['pip', 'install', 'pyyaml'])
    import yaml


class LoadConfParams:

    def __init__(self):
        with open('config.yml', 'r') as file_:
            self.cfg = yaml.safe_load(file_)
        file_.close()

        try:
            self.lynis_info = self.cfg.get('lynis')
            self.hostnames_path = self.cfg.get('hostnames')['hostnames_path']
            self.john_info = self.cfg.get('john')
            self.scan_info = self.cfg.get('portscan')
        except yaml.YAMLError:
            logging.error('Could not load info - check YAML file')
            exit(1)

    def get_lynis_run_file(self):
        try:
            lynis_run_file = self.lynis_info['lynis_file']
        except yaml.YAMLError:
            logging.error('Could not load Lynis file - check YAML file')
            exit(1)

        return lynis_run_file

    def get_lynis_repo(self):
        try:
            lynis_repo = self.lynis_info['repo']
        except yaml.YAMLError:
            logging.error('Could not load Lynis repo - check YAML file')
            exit(1)

        return lynis_repo

    def get_lynis_local_report(self):
        try:
            lynis_local_report = self.lynis_info['local_report']
        except yaml.YAMLError:
            logging.error('Could not load Lynis local report - check YAML file')
            exit(1)

        return lynis_local_report

    def get_lynis_log(self):
        try:
            lynis_log = self.lynis_info['report_path']
        except yaml.YAMLError:
            logging.error('Could not load Lynis log folder - check YAML file')
            exit(1)

        return lynis_log

    def get_lynis_final_report(self):
        try:
            lynis_final_report = self.lynis_info['report_file_name']
        except yaml.YAMLError:
            logging.error('Could not load Lynis final report - check YAML file')
            exit(1)

        return lynis_final_report

    def get_ip_list(self):
        try:
            with open(self.hostnames_path, 'r') as hn:
                hostnames_dict = yaml.safe_load(hn)
            hn.close()
        except yaml.YAMLError:
            logging.error('Could not load hosts and containers IPs - check YAML file')
            exit(1)

        with open('ip_list', 'w+') as infile:
            for key in hostnames_dict:
                infile.write(hostnames_dict.get(key).get('ansible_host') + '\n')
        
        infile.close()
 
        return os.path.abspath('ip_list')

    def get_shadow_file(self):
        try:
            shadow_file = self.john_info['shadow']
        except yaml.YAMLError:
            logging.error('Could not load shadow file - check YAML file')
            exit(1)

        return shadow_file

    def get_passwd_file(self):
        try:
            passwd_file = self.john_info['passwd']
        except yaml.YAMLError:
            logging.error('Could not load passwd file - check YAML file')
            exit(1)

        return passwd_file

    def get_scan_xml_results(self):
        try:
            scan_xml_results = self.scan_info['xmlresult_file']
        except yaml.YAMLError:
            logging.error('Could not load scan xml file - check YAML file')
            exit(1)

        return scan_xml_results

    def get_scan_final_results(self):
        try:
            scan_final_results = self.scan_info['finalresult_file']
        except yaml.YAMLError:
            logging.error('Could not load scan final file - check YAML file')
            exit(1)

        return scan_final_results

