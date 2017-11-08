#!/usr/bin/env python
#coding: utf_8

import smtplib
import sys

txtparam = sys.argv[1]
fromaddr = ''
toaddr = ''
subj = 'Sony Abuse'
msg_txt = 'Notice:\n\n ' +  txtparam + '\n\nBye!'
msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( fromaddr, toaddr, subj, msg_txt)

username = 'sony_acc'
password = ''

server = smtplib.SMTP('mail.:25')
server.set_debuglevel(1)
server.starttls()
server.login(username, password)
server.sendmail(fromaddr, toaddr, msg)
server.quit()
