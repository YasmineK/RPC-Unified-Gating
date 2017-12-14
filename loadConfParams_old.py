import os
import logging
import yaml


class LoadConfParams:

    def __init__(self):
        with open('config.yml', 'r') as file_:
            try:
                self.cfg = yaml.safe_load(file_)
            except yaml.YAMLError:
                logging.error('Could not load info - check YAML file')
                exit(1)
        # file_.close()  -- with actually cleans up automatically / no need for this line

        self.lynis_info = self.cfg.get('lynis')
        self.hostnames_path = self.cfg.get('hostnames')['hostnames_path']
        self.local_hostnames_path =self.cfg.get('hostnames')['local_hostnames_path']
        self.john_info = self.cfg.get('john')
        self.scan_info = self.cfg.get('portscan')
        self.file = self.lynis_info['lynis_file']

    def get_lynis_run_file(self):
        return self.lynis_info['lynis_file']

    def get_lynis_repo(self):
        return self.lynis_info['repo']

    def get_lynis_local_report(self):
        return self.lynis_info['local_report']

    def get_lynis_log(self):
        return self.lynis_info['report_path']

    def get_lynis_final_report(self):
        return self.lynis_info['report_file_name']

    def get_ip_list_on_remote_host(self):
        # Loads yaml inventory file
        try:
            with open(self.hostnames_path, 'r') as hn:
                hostnames_dict = yaml.safe_load(hn)
        except yaml.YAMLError:
            logging.error('Could not load hosts and containers IPs - check YAML file')
            exit(1)

        with open('ip_list', 'w+') as infile:
            for key in hostnames_dict:
                infile.write(hostnames_dict.get(key).get('ansible_ssh_host') + '\n')
        
        return os.path.abspath('ip_list')

    def get_ip_list(self):
        # Loads yaml inventory file
        try:
            with open(self.local_hostnames_path, 'r') as hn:
                hostnames_dict = yaml.safe_load(hn)
        except yaml.YAMLError:
            logging.error('Could not load hosts and containers IPs - check YAML file')
            exit(1)

        with open('ip_list', 'w+') as infile:
            for key in hostnames_dict:
                infile.write(hostnames_dict.get(key).get('ansible_ssh_host') + '\n')

        return os.path.abspath('ip_list')

    def get_shadow_file(self):
        return self.john_info['shadow']

    def get_passwd_file(self):
        return self.john_info['passwd']

    def get_scan_xml_results(self):
        return self.scan_info['xmlresult_file']

    def get_scan_final_results(self):
        return self.scan_info['finalresult_file']

