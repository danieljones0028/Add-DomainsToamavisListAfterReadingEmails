# -*- coding: utf-8 -*-

import subprocess
from subprocess import check_output, CalledProcessError, PIPE
import os
import sys
import socket
import logging
import dns.resolver
import re
import json

logging.basicConfig(filename='mailboxantispam.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

zmprov = '/opt/zimbra/bin/zmprov'
zmmailbox = '/opt/zimbra/bin/zmmailbox'
domain = 'empresalab.com.br'
account = 'spam_collection'

# change to your language
to = 'De '
To = 'De'

def GetAllDomains():

    myDomains = []

    try:
        c = '%s gad' % (zmprov)
        s = subprocess.check_output([c], shell=True)
        s = s.split('\n')

        for myDomain in s:
            if myDomain != '':
                myDomains.append(myDomain)

        return myDomains

    except Exception as e:
        logging.error('An error occurred while trying to get domains')
        logging.error(e)
        print('An error occurred while trying to get domains')
        print(e)

def getMsid():

    try:

        messageIds = []

        c = '%s -z -m %s@%s s -v Spam' % (zmmailbox, account, domain)
        s = subprocess.check_output([c], shell=True)
        o = json.loads(s)
        i = o.get('hits')

        for item in i:
            n = item.get('messageIds')
            n = n[0]
            n = str(n)
            messageIds.append(n)

        if len(messageIds) == 0:
            logging.info('Nenhum email encontrado, finalizando execução')
            print('Nenhum email encontrado, finalizando execução')
            sys.exit(0)

        messageIds.sort()

        try:

            obj = []
            adresses = []

            for msgid in messageIds:
                c = '%s -z -m %s@%s gm %s' % (zmmailbox, account, domain, msgid)
                s = subprocess.check_output([c], shell=True)
                obj.append(s)

            for item in obj:
                x = re.findall(r'[\w\.-]+@[\w.-]+', item)
                if x:
                    y = x[2]
                    adresses.append(y)

            adresses.sort()

            return adresses

        except Exception as e:
            logging.error('Ocorreu um erro na definição getMisd ao tentar criar a lista adresses.')
            logging.error(e)
            print('Ocorreu um erro na definição getMisd ao tentar criar a lista adresses.')
            print(e)

    except Exception as e:
        logging.error('Ocorreu um erro na definição getMisd ao tentar criar a lista messageIds.')
        logging.error(e)
        print('Ocorreu um erro na definição getMisd ao tentar criar a lista messageIds.')
        print(e)

def getDomainFromAddress():

    try:

        gotDomain = []
        adresses = getMsid()

        for item in adresses:
            try:
                for domainAdress in item.splitlines():
                    u, d = domainAdress.split("@", 2)
                    if d and u:
                        gotDomain.append(d)

            except Exception as e:
                print(e)

        unique_list = []

        for item in gotDomain:
            if item not in unique_list:
                unique_list.append(item)

        unique_list.sort()

# Teste trecho do codigo para validação
        myDomains = GetAllDomains()

        for item in myDomains:
            if item in unique_list:
                unique_list.remove(item)
# Teste trecho do codigo para validação

        return unique_list

    except Exception as e:
        print(e)

def collectsCurrentList():

    cmd_awk = "'{print $2}'"
    cmd_sed = "'/^$/d'"

    generateFileFromCurrentList = '%s gd %s amavisBlacklistSender | grep -v %s | awk %s | sed %s > /tmp/amavis_%s_blacklist_fromMailSpam' % (zmprov, domain, domain, cmd_awk, cmd_sed, domain)
    subprocess.call(generateFileFromCurrentList, shell=True)

    try:

        if os.path.exists('/tmp/amavis_%s_blacklist_fromMailSpam' % (domain)):
            amavisCurrentList = ('/tmp/amavis_%s_blacklist_fromMailSpam' % (domain))
            amavisGrossCurrentList = open(amavisCurrentList, 'r').read().split('\n')
            amavisGrossCurrentList.sort()

            amavisList = []

            for item in amavisGrossCurrentList:
                if item != "":
                    amavisList.append(item)
                    logging.info('Item found on amavis and will be added to a list for future comparisons: %s' % (item))
                    print('Item found on amavis and will be added to a list for future comparisons: %s' % (item))
        else:
            logging.error('Current list not found. Call support.')
            print('Current list not found. Call support.')
            sys.exit(1)

        amavisList.sort()

        return amavisList

    except Exception as e:
        logging.error('Definition error collectsCurrentList')
        logging.error(e)
        print('Definition error collectsCurrentList')
        print(e)

def comparingLists(current, check):

    global membershipList

    membershipList = []

    try:
        for item in check:
            if item not in current:
                logging.info('adding item to membership list: %s' % (item))
                print('adding item to membership list: %s' % (item))
                membershipList.append(item)

    except Exception as e:
        logging.error('definition error comparingLists: %s' % (e))
        print('definition error comparingLists: %s' % (e))

    membershipList.sort()

    return membershipList

def searchSolveIpFromMx(data):
    try:
        list_Ips = []
        list_Mx = []
        unique_List = []
        for mx_s in data:
            for mx in dns.resolver.query(mx_s, 'MX'):
                mx = mx.to_text()
                try:
                    for mx_Name in mx.splitlines():
                        k, v = mx_Name.split(" ", 2)
                        list_Mx.append(v)
                        logging.info('MX added to list: %s' % (v))
                        print('MX added to list: %s' % (v))

                except ValueError as e:
                    logging.error('An error occurred while trying to add MX to list')
                    logging.error(e)
                    print('An error occurred while trying to add MX to list')
                    print(e)

            for ips in list_Mx:
                try:
                    if socket.gethostbyname(ips):
                        logging.info('MX ip found: %s' % (ips))
                        print('MX ip found: %s' % (ips))
                        ip = socket.gethostbyname(ips)
                        list_Ips.append(ip)
                        logging.info('MX ip added to list')
                        print('MX ip added to list')
                    else:
                        logging.error('Could not find MX ip: %s' % (ips))
                        print('Could not find MX ip: %s' % (ips))

                except Exception as e:
                    logging.warning('Could not find MX ip: %s' % (ips))
                    logging.error(e)
                    print('Could not find MX ip: %s' % (ips))
                    print(e)

    except Exception as e:
        logging.error('definition searchSolveIpFromMx error')
        logging.error(e)
        print('definition searchSolveIpFromMx error')
        print(e)

    for item in list_Ips:
        if item not in unique_List:
            logging.info('removing repeated list items: %s' % (item))
            print('removing repeated list items: %s' % (item))
            unique_List.append(item)

    unique_List.sort()

    ListOfIPSFoundFromCollectedDomains = unique_List

    return ListOfIPSFoundFromCollectedDomains

def addingDomains(data):

    try:

        if not len(data) == 0:
            for domain_Membership in data:
                c = '%s md %s +amavisBlacklistSender %s' % (zmprov, domain, domain_Membership)
                subprocess.call(c, shell=True)
                logging.info('Adding %s to amavis' % (domain_Membership))
                print('Adding %s to amavis' % (domain_Membership))
        else:
            logging.info('No new domain entries.')
            print('No new domain entries.')

    except Exception as e:
        logging.error('Definition addingDomains error')
        logging.error(e)
        print('Definition addingDomains error')
        print(e)


comparingLists(collectsCurrentList(), getDomainFromAddress())
searchSolveIpFromMx(membershipList)
addingDomains(membershipList)
