from subprocess import call

call(['find', '.', '-name', '*.rec', '-delete'])
call(['find', '.', '-name', '*.log', '-delete'])
call(['find', '.', '-name', 'out*', '-delete'])
call(['find', '.', '-name', 'result*', '-delete'])
call(['find', '.', '-name', 'lynis*', '-delete'])
call(['rm', '-rf', 'lynis'])
call(['rm', 'container_list.txt'])
with open('temp.txt') as t:
    for line in t:
        line =  line.rstrip()
        print line
        #call(['lxc-attach', '-n', line, '--', 'find', '.', '-name', '*.rec'])
        call(['lxc-attach', '-n', line, '--', 'rm', '-rf', 'lynis'])
        call(['lxc-attach', '-n', line, '--', 'find', '.', '-name', 'lynis*', '-delete']) 
        call(['lxc-attach', '-n', line, '--', 'find', '.', '-name', '*.rec', '-delete'])
        print 'remove .rec'
        call(['lxc-attach', '-n', line, '--', 'find', '.', '-name', '*.log', '-delete'])
        call(['lxc-attach', '-n', line, '--', 'find', '.', '-name', 'out*', '-delete'])
        call(['lxc-attach', '-n', line, '--', 'find', '.', '-name', 'result*', '-delete'])
        #break
    t.close()    
