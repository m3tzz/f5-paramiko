# author: Ruben Barbosa
# version: 1.0
# Description: Send configs to F5 Device and Rollback in case something went wrong

import paramiko
import time
import getpass
import sys
import os

# function to read files
def load_file_host_config(host_file):

    ##### Read Host files ######
    file = open(host_file, 'r')
    ###### split the lines via /n #####
    host_tmp = file.read().split('\n')
    return host_tmp

def load_file_vip_config(vip_file):

    ##### Read vip files ######
    file = open(vip_file, 'r')
    ###### split the lines via /n #####
    vip_tmp = file.read().split('\n')
    #vip_tmp = file.read()
    return vip_tmp

# function to print menu
def print_menu():

    print"\n"
    print"##################### F5 #####################\n"
    print"Please choose one of the otpions below:\n"
    print"[1] - Generate the configs of new vip.\n"
    print"[2] - Send configs to F5.\n"
    print"[3] - Rollback configs to F5. \n\n"


# function to option choosen
def option_choosen(option,f5_ip):
     try :
            if (option == 1):
                print "\n###### GENERATE CONFIGS OF NEW VIP ########\n"
                # Passagem Parametros
                numberSVRS = int(raw_input('\ninsert number of servers:'))
                nameSVRS = raw_input('\ninsert name of servers:')
                protocol = raw_input('\ninsert name of protocol[e.g - TCP,SSL,HTTP]:')
                serviceSVRS = int(raw_input('\ninsert service running on servers[e.g - 8080,8443,9410]:'))
                namePOOL = raw_input('\ninsert name of POOL:')
                newvip = raw_input('\ninsert name of New Vip[TLA of Prodcut]:')
                vipip = raw_input('\ninsert IP of New Vip:')
                #Export the configs to File
                f1 = open('CONFIGS_OF_'+newvip.upper()+'.txt', 'w')
                sys.stdout = f1
                print newVip_F5(numberSVRS, nameSVRS, protocol,serviceSVRS, namePOOL, newvip, vipip)
                f1.close()
                #Export the rollback to File
                f2 = open('ROLLBACK_OF_'+newvip.upper()+'.txt', 'w')
                sys.stdout = f2
                print rollback_newVip_F5(numberSVRS, nameSVRS,serviceSVRS, namePOOL, newvip, vipip)
                f2.close()
            elif (option == 2):
                print "\n###### SEND CONFIG TO F5 - "+f5_ip[1]+" ########\n"
                send_config_to_f5(ip,username,password,buffer_size,waittime,file_vip)
            elif (option == 3):
                print "\n###### ROLLBACK CONFIG TO F5 - "+f5_ip[1]+" ########\n"
                rollback_config_to_f5(ip,username,password,buffer_size,waittime,file_rollback_vip)
            else:
                print "\nSorry this option does not exist.\nThe script will be terminated!\n"
                sys.exit(0)
     except ValueError:
        print "\nSorry this option does not exist: "+ValueError+"\n.The script will be terminated!\n"
        sys.exit(0)

# function to send the configs to device
def send_config_to_f5(ip,username,password,buffer_size,waittime,file_vip):

    try:
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()
        # Automatically add untrusted hosts (make sure okay for security policy in your environment)
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # initiate SSH connection
        remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
        print "SSH connection established to %s" % ip+"\n"
        # Use invoke_shell to establish an 'interactive session'
        remote_conn = remote_conn_pre.invoke_shell()
        print "Interactive SSH session established\n"
    except paramiko.AuthenticationException:
        print "\nAuthentication Failed\n"
        sys.exit(0)
    except paramiko.SSHException:
        print "\nIssues with SSH service\n"
        sys.exit(0)
    except socket.error,e:
        print "\nConnection Error\n"
        sys.exit(0)

    # Strip the initial router prompt
    output = remote_conn.recv(buffer_size)
    # See what we have
    print output
    # Now let's try to send the NS a command
    enter="\n"
    # Read the content of the file
    for line in file_vip:
        if not line.strip():  # ignore blank lines
            continue
        elif line.startswith('#'):  # ignore comments
            continue
        else:   # process the line
            remote_conn.send(line+enter)

    remote_conn.send("save sys config")
    # Wait for the command to complete
    time.sleep(waittime)

    output = remote_conn.recv(buffer_size)

    # See what we have
    print output
    remote_conn.close()

def rollback_config_to_f5(ip,username,password,buffer_size,waittime,file_rollback_vip):

    try:
        # Create instance of SSHClient object
        remote_conn_pre = paramiko.SSHClient()
        # Automatically add untrusted hosts (make sure okay for security policy in your environment)
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # initiate SSH connection
        remote_conn_pre.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)
        print "SSH connection established to %s" % ip+"\n"
        # Use invoke_shell to establish an 'interactive session'
        remote_conn = remote_conn_pre.invoke_shell()
        print "Interactive SSH session established\n"
    except paramiko.AuthenticationException:
        print "\nAuthentication Failed\n"
        sys.exit(0)
    except paramiko.SSHException:
        print "\nIssues with SSH service\n"
        sys.exit(0)
    except socket.error,e:
        print "\nConnection Error\n"
        sys.exit(0)

    # Strip the initial router prompt
    output = remote_conn.recv(buffer_size)
    # See what we have
    print output
    # Now let's try to send the NS a command
    enter="\n"
    # Read the content of the file
    for line in file_rollback_vip:
        if not line.strip():  # ignore blank lines
            continue
        elif line.startswith('#'):  # ignore comments
            continue
        else:   # process the line
            remote_conn.send(line+enter)
            #time.sleep(3)
            #output = remote_conn.recv(buffer_size)
            #if output.find("Done") == -1:          # Check for failure note -1 is the position
            #    print output
            #    print "ERROR - Command failed:\n Finish program"
            #    sys.exit(0)
    remote_conn.send("save sys config")
    # Wait for the command to complete
    time.sleep(waittime)

    output = remote_conn.recv(buffer_size)

    # See what we have
    print output

    remote_conn.close()

# function to generate the configs of new vip
def newVip_F5(numberSVRS, nameSVRS, protocol,serviceSVRS, namePOOL, newvip, vipip):

    if (protocol == 'HTTP' or protocol == 'http'):

        i = 0
        j = 0
        print "New Internal VIP Configuration - IE1"
        print "#Create Nodes"
        for i in range(0, numberSVRS):
            i += 1
            print "create ltm node "+nameSVRS+"00"+str(i)+" { address <IP> }"
        print "#Create Pool for Nodes"
        print "create ltm pool "+namePOOL

        print "#load-balancing-mode"
        print "modify ltm pool"+namePOOL+" load-balancing-mode rounde-robin"
        for j in range(0, numberSVRS):
            j += 1
            print "modify ltm pool "+namePOOL+" members add { "+nameSVRS+"00"+str(j)+":"+str(serviceSVRS)+"}"
        print "#Bind Monitor to Pool"
        print "modify ltm pool "+namePOOL+" monitor tcp"

        print "#Create the Virtual Address for VIP"
        print "create ltm virtual-address /Common/"+vipip

        print "#Create the HTTP VIP"
        print "#Define name of VIP"
        print "create ltm virtual /Common/"+newvip+".<domain>"

        print "#Put the IP to the VIP"
        print "modify ltm virtual /Common/"+newvip+".<domain> destination /Common/"+vipip+":80 mask 255.255.255.255"
        print "modify ltm virtual /Common/"+newvip+".<domain> ip-protocol tcp"
        print "modify ltm virtual /Common/"+newvip+".<domain> profiles replace-all-with { /Common/tcp { } }"
        print "modify ltm virtual /Common/"+newvip+".<domain> profiles add { /Common/http { } }"
        print "modify ltm virtual /Common/"+newvip+".<domain> profiles add { oneconnect }"
        print "modify ltm virtual /Common/"+newvip+".<domain> pool /Common/"+namePOOL
        print "modify ltm virtual /Common/"+newvip+".<domain> source-address-translation { type automap }"
        print "modify ltm virtual /Common/"+newvip+".<domain> translate-address enabled"
        print "modify ltm virtual /Common/"+newvip+".<domain> translate-port enabled"

        print "# Create the HTTPS VIP"
        print "#Define name of VIP"
        print "create ltm virtual /Common/"+newvip+".<domain>-443"

        print "#Put the IP to the VIP"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 destination /Common/"+vipip+":443 mask 255.255.255.255"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 ip-protocol tcp"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 profiles replace-all-with { /Common/tcp { } }"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 profiles add { /Common/http { } }"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 profiles add { <certificate> { context clientside } }"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 profiles add { oneconnect } "
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 pool /Common/"+namePOOL
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 source-address-translation { type automap}"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 translate-address enabled"
        print "modify ltm virtual /Common/"+newvip+".<domain>-443 translate-port enabled"

        print "# Save the config to bigip.conf"
        print "save sys config"


    elif (protocol != 'HTTP' or protocol != 'http'):

        i = 0
        j = 0
        print "New Internal VIP Configuration - IE1"
        print "#Create Nodes"
        for i in range(0, numberSVRS):
            i += 1
            print "create ltm node "+nameSVRS+"00"+str(i)+" { address  }"
        print "#Create Pool for Nodes"
        print "create ltm pool "+namePOOL

        print "#load-balancing-mode"
        print "modify ltm pool"+namePOOL+" load-balancing-mode rounde-robin"
        for j in range(0, numberSVRS):
            j += 1
            print "modify ltm pool "+namePOOL+" members add { "+nameSVRS+"00"+str(j)+":"+str(serviceSVRS)+"}"
        print "#Bind Monitor to Pool"
        print "modify ltm pool "+namePOOL+" monitor tcp"

        print "#Create the Virtual Address for VIP"
        print "create ltm virtual-address /Common/"+vipip

        print "#Create the TCP VIP"
        print "#Define name of VIP"
        print "create ltm virtual /Common/"+newvip+".<domain>"

        print "#Put the IP to the VIP"
        print "modify ltm virtual /Common/"+newvip+".<domain> destination /Common/" + vipip + ":" +str(serviceSVRS)+ " mask 255.255.255.255"
        print "modify ltm virtual /Common/"+newvip+".<domain> ip-protocol tcp"
        print "modify ltm virtual /Common/"+newvip+".<domain> profiles add { /Common/tcp { } }"
        print "modify ltm virtual /Common/"+newvip+".<domain> profiles add { oneconnect }"
        print "modify ltm virtual /Common/"+newvip+".<domain> pool /Common/"+namePOOL
        print "modify ltm virtual /Common/"+newvip+".<domain> source-address-translation { type automap }"
        print "modify ltm virtual /Common/"+newvip+".<domain> translate-address enabled"
        print "modify ltm virtual /Common/"+newvip+".<domain> translate-port enabled"

        print "# Save the config to bigip.conf"
        print "save sys config"

    else:
        print "\nSorry this option does not exist.\nThe script will be terminated!\n"
        sys.exit(0)

def rollback_newVip_F5(numberSVRS, nameSVRS, serviceSVRS, namePOOL, newvip, vipip):

        print "delete ltm virtual /Common/"+newvip+".<domain>"
        print "delete ltm virtual-address /Common/"+vipip
        print "delete ltm pool "+namePOOL
        for i in range(0, numberSVRS):
            i += 1
            print "delete ltm node "+nameSVRS+"00"+str(i)+" { address <IP> }"
        print "save sys config"


if __name__ == '__main__':

    ########### read info from host file ############
    host_tmp = load_file_host_config('hosts_file.txt')

    ####### LOGIN TACACS ########
    print "\n##################### TACACS Login #####################\n"
    username = raw_input('\ninsert your username:')
    password = getpass.getpass("Enter your password:")
    ####### END LOGIN TACACS ########

    ###### print menu ######
    print_menu()
    ###### option ######
    option = int(raw_input("[option]:"))

    ######### split IP and Name of NS and run the instruction for all LBs on file #########
    for f5_ip in host_tmp:
        if len(f5_ip) <= 2:
            continue
        #### define what is IP of NS #####
        f5_ip = str(f5_ip).split(' ')
        ############ read info from config file ############
        file_vip = load_file_vip_config('newconfig.txt')
        #file_vip = file_vip_tmp.replace('{ip}','1.1.1.1')
        ############ read info from rollback file ############
        file_rollback_vip = load_file_vip_config('rollback.txt')

        ##### IP of LB #####
        ip=f5_ip[0]

        buffer_size = 1000000
        waittime = 6

        ##### Option Choosen ######
        option_choosen(option,f5_ip)


    sys.exit(0)
