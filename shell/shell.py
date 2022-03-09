#! /usr/bin/env python3
 
import os, sys, time, re


env_key = os.environ
env_key["ShellStart"] = "$ "    #modify the environment object

while True:
    os.write(1,(env_key["ShellStart"]).encode())
    input = os.read(0, 100).decode()
    input = input[:-1]#remove \n

    if 'cd' in input:             #check whether cd exists at index 0
        input = re.split(":? ", input, 1)    #split command and pathname
        if "cd.." in input[0]:
            print(os.getcwd())
            os.chdir(os.getcwd().rsplit('/', 1)[0])
            print(os.getcwd())
            continue
        else:
            os.chdir(input[1])
            print(os.getcwd())
            continue
    if "exit" in input:
        print("Exiting shell...")
        break
    
   
    args = input.split()
    
    pid = os.getpid()
    os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
        # args = ["wc", "p3-exec.py"]
    elif rc == 0:                   # child
        
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
            try:
                print(os.environ)
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly

        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())
    input = "exit"
