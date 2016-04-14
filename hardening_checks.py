import os
import subprocess
from subprocess import call
from threading import Timer

counter = 0


def run_lynis():
    # this first part runs lynis on the main host ....
    call(['git', 'clone', 'https://github.com/CISOfy/lynis'])
    os.chdir('lynis')
    call(['./lynis', 'audit', 'system', '-V'])
    os.chdir('../')
    # remember to remove lynis after use

     # implements "cd" as directory needs to be changed in the
     # containers for ./lynis to run
    lynis = open('lynis.sh', 'w+')
    lynis.write('#!/bin/bash')
    lynis.write('\n\n')
    lynis.write('pushd lynis \n')
    lynis.write('\t ./lynis $@ \n')
    lynis.write('popd')
    lynis.close()

    call(['chmod', '0700', 'lynis.sh'])
    
    print 'NOW RUNNING LYNIS ON CONTAINERS'	

    # ... the second part of the run include running lynis on containers
    with open('container_list.txt') as cl:
        for line in cl:
            line = line.rstrip()
            print line
            call(['scp', '-r', 'lynis/', 'root@'+line+':'])
            call(['scp', 'lynis.sh', 'root@'+line+':'])
            call(['lxc-attach', '-n', line, '--', './lynis.sh', 'audit',
                  'system', '-Q'])
            #break
        cl.close()


def get_container_list():
    container_list = open('container_list.txt', 'w+')
    call(['lxc-ls'], stdout=container_list)
    container_list.close()


def run_john():
    shadow_file = '/etc/shadow'
    passwd_file = '/etc/passwd'

    # this first part runs John on main host
    exec_call(None, passwd_file, shadow_file)

    # now run John on from all containers

    with open('container_list.txt') as cl:
        for line in cl:
            line = line.rstrip()
            exec_call(line, passwd_file, shadow_file)
        cl.close()


def exec_call(container_name, passwd_file, shadow_file):
    global counter
    out = open('out_' + str(counter) + '.txt', 'w+')
    result = open('result_' + str(counter) + '.txt', 'w+')

    if container_name is not None:
        print 'RUNNING JOHN ON CONTAINER: ' + container_name
        call(['lxc-attach', '-n', container_name, '--', 'apt-get',
             'install', '-y', 'john'])
        call(['lxc-attach', '-n', container_name, '--', 'unshadow',
              passwd_file, shadow_file], stdout=out)
        call(['scp', 'out_' + str(counter) + '.txt', 'root@'+container_name+':'])
        process = subprocess.Popen(['lxc-attach', '-n', container_name, '--',
                                    'john', '--session=' + str(counter), 'out_' +
                                    str(counter) + '.txt'], stdout=result)
    else:
        print 'RUNNING JOHN ON HOST'
        try:
            call(['unshadow', passwd_file, shadow_file], stdout=out)
        except OSError as exc:
            if exc.errno == os.errno.ENOENT:       # program not installed
                call(['apt-get', 'install', '-y', 'john'])

        process = subprocess.Popen(['john', '--session=' + str(counter), 'out_' + str(counter) + '.txt'],
                                   stdout=result)

    timer = Timer(600, kill_process, [process])
    timer.start()

    counter += 1
    out.close()
    result.close()


def kill_process(process):
    process.kill()
    print 'KILLED - JOHN FINISHED RUNNING ON CONTAINER ' + str(counter) + '\n'


def main():
    get_container_list()
    run_lynis()
    run_john()

if __name__ == "__main__":
    main()
