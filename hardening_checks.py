import os
import subprocess
import time
from subprocess import call
from paramiko import SSHClient
from paramiko import AutoAddPolicy
from threading import Timer

try:
    import yaml
except ImportError:
    call(['pip', 'install', 'pyyaml'])
    import yaml
try:
    import sh
except ImportError:
    call(['pip', 'install', 'sh'])
    import sh
from scp import SCPClient

counter = 0
lynis_repo = ''
lynis_run_file = None
shadow_file = None
passwd_file = None
container_list_file = None
hostnames_dict = None
hostnames_list = []
lynis_log_folder = ''
local_lynis_report = ''
report_file_name = ''



def load_config():
    global lynis_repo, lynis_run_file, shadow_file, passwd_file, \
        container_list_file, hostnames_dict, local_lynis_report, lynis_log_folder, \
        report_file_name

    with open('config.yml', 'r') as file_:
        cfg = yaml.safe_load(file_)
    file_.close()

    try:
        lynis_info = cfg.get('lynis')
        lynis_repo = lynis_info['repo']
        lynis_run_file = lynis_info['lynis_file']
        local_lynis_report = lynis_info['local_report']
        lynis_log_folder = lynis_info['report_path']
        report_file_name = lynis_info['report_file_name']
    except yaml.YAMLError:
        print 'Could not load Lynis info - check YAML file'
        exit()

    print 'lynis repo is: ' + lynis_repo

    try:
        john_info = cfg.get('john')
        shadow_file = john_info['shadow']
        passwd_file = john_info['passwd']
    except yaml.YAMLError:
        print 'Could not load John the Ripper config - check YAML file'
        exit()

    try:
        hostnames_path = cfg.get('hostnames')['hostnames_path']
        with open(hostnames_path, 'r') as hn:
            hostnames_dict = yaml.safe_load(hn)
        hn.close()
    except yaml.YAMLError:
        print 'Could not load Containers config - check YAML file'
        exit()

def get_ssh_client():
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())

    return client


def get_hostnames_list():
    global hostnames_list

    for key in hostnames_dict:
        hostnames_list.append(key)


def get_lynis_report(node):
    global report_file_name

    report_file = open(report_file_name, 'w+')
    report_file.close()

    sh.grep(sh.cat(local_lynis_report), 'warning', _out=report_file_name)

    statinfo = os.stat(report_file_name)
    if statinfo.st_size > 0:
        os.rename(report_file_name, os.path.join(lynis_log_folder, report_file_name + '_' + node))
    else:
        os.remove(report_file_name)



def run_lynis_deployment_host(repo):
    call(['git', 'clone', repo])
    os.chdir('lynis')
    call(['./lynis', 'audit', 'system', '-q'])  # logs in /var/log/lynis.log and lynis-report.dat
    os.chdir('../')

    get_lynis_report("deployment_host")


def run_lynis_in_env():

    # implements "cd" as directory needs to be changed in the
    # containers for ./lynis to run
    lynis = open(lynis_run_file, 'w+')
    lynis.write('#!/bin/bash')
    lynis.write('\n\n')
    lynis.write('pushd lynis \n')
    lynis.write('\t ./lynis $@ \n')
    lynis.write('popd')
    lynis.close()

    call(['chmod', '0700', lynis_run_file])


    print 'NOW RUNNING LYNIS IN WHOLE ENV'

    for node in hostnames_list:
        ssh = get_ssh_client()
        ssh.connect(node, username='root', key_filename='/root/.ssh/id_rsa')
        scp = SCPClient(ssh.get_transport())
        scp.put('lynis/', 'lynis/', recursive=True)
        scp.put(lynis_run_file, lynis_run_file)
        stdin, stdout, stderr = ssh.exec_command('./lynis.sh audit system -q')
        # wait for command to finish running before closing channel
        while not stdout.channel.exit_status_ready():
            print u'Running lynis on {0:s}... \n'.format(node)
            time.sleep(20)

        ssh.close()

        # now log warnings for review
        get_lynis_report(node)


def run_lynis():
    # this first part runs lynis on the main host ....
    run_lynis_deployment_host(lynis_repo)
    # remember to remove lynis after use

    run_lynis_in_env()


def run_john():        # ignored for now

    # this first part runs John on main host
    exec_call(None, passwd_file, shadow_file)

    # now run John on from all containers
    with open(container_list_file) as cl:
        for line in cl:
            line = line.rstrip()
            exec_call(line, passwd_file, shadow_file)
        cl.close()


def exec_call(container_name, passwd, shadow):
    global counter
    counter = 0
    out = open('out_' + str(counter) + '.txt', 'w+')
    result = open('result_' + str(counter) + '.txt', 'w+')

    if container_name is not None:
        print 'RUNNING JOHN ON CONTAINER: ' + container_name
        call(['lxc-attach', '-n', container_name, '--', 'apt-get',
             'install', '-y', 'john'])
        call(['lxc-attach', '-n', container_name, '--', 'unshadow',
              passwd, shadow], stdout=out)
        call(['scp', 'out_' + str(counter) + '.txt', 'root@'+container_name])      # removed : here as well:
        process = subprocess.Popen(['lxc-attach', '-n', container_name, '--',
                                    'john', '--session=' + str(counter), 'out_' +
                                    str(counter) + '.txt'], stdout=result)
    else:
        print 'RUNNING JOHN ON HOST'
        try:
            call(['unshadow', passwd, shadow], stdout=out)
        except OSError as exc:
            if exc.errno == os.errno.ENOENT:       # program not installed
                call(['apt-get', 'install', '-y', 'john'])

        process = subprocess.Popen(['john', '--session=' + str(counter), 'out_' + str(counter) + '.txt'],
                                   stdout=result)

    timer = Timer(600, kill_john_process, [process])
    timer.start()

    counter += 1
    out.close()
    result.close()


def kill_john_process(process):
    process.kill()
    print 'KILLED - JOHN FINISHED RUNNING ON CONTAINER ' + str(counter) + '\n'


def main():
    load_config()
    get_hostnames_list()
    # prepare log folder for lynis report
    os.makedirs(lynis_log_folder)
    run_lynis()
    # run_john()


if __name__ == "__main__":
    main()
