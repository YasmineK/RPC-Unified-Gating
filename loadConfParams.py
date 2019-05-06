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

        # lynis config
        self.lynis_info = self.cfg.get('lynis')
        self.lynis_file = self.lynis_info['lynis_file']
        self.lynis_repo = self.lynis_info['repo']
        self.lynis_local_report = self.lynis_info['local_report']
        self.lynis_log = self.lynis_info['report_path']
        self.lynis_final_report = self.lynis_info['report_file_name']

        # john config
        self.john_info = self.cfg.get('john')
        self.shadow_file = self.john_info['shadow']
        self.passwd_file = self.john_info['passwd']

        # scan config
        self.scan_info = self.cfg.get('portscan')
        self.scan_xml_results = self.scan_info['xmlresult_file']
        self.scan_final_results = self.scan_info['finalresult_file']

        self.hostnames_path = self.cfg.get('hostnames')['hostnames_path']
        self.local_hostnames_path = self.cfg.get('hostnames')['local_hostnames_path']

    def _load_yml_file(self, file_path):
        try:
            with open(file_path, 'r') as file_:
                return yaml.safe_load(file_)
        except yaml.YAMLError:
            logging.error('Could not load hosts and containers IPs - check YAML file')
            exit(1)

    def get_hostnames_list(self):
        # Loads yaml inventory file
        return self._load_yml_file(self.hostnames_path).keys()  # returns a list of hostnames' keys

    def _get_ip_list(self, file_path):
        # Loads yaml inventory file
        hostnames = self._load_yml_file(file_path)

        with open('iplist', 'w+') as infile:
            for host in hostnames.values():
                infile.write(host['ansible_ssh_host'] + '\n')

        return os.path.abspath('iplist')

    def get_local_ip_list(self):
        return self._get_ip_list(self.local_hostnames_path)

    def get_remote_ip_list(self):
        return self._get_ip_list(self.hostnames_path)

