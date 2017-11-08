#!/usr/bin/env python
#coding: utf_8

from datetime import datetime, timedelta
import subprocess
import smtplib
import sys

NATS_LIST = ['213.21.32.', '213.21.33.', '213.21.34.', '213.21.35.', '213.21.36.', '213.21.37.', '213.21.38.', '213.21.39.', '213.21.40.', '213.21.41.', '213.21.42.', '213.21.43.', '213.21.44.', '213.21.45.', '213.21.46.', '213.21.47.', '213.21.56.']

# Поис индентификатора письма
print('=> Поис индентификатора письма')
email_id = "ssh USERNAME@mail \"sudo /opt/zimbra/bin/zmmailbox -z -m sony_acc@DOMAIN s in:Inbox | grep Play | awk '{print \$2}' | tr -d -\""
proc = subprocess.Popen(email_id, shell=True, stdout=subprocess.PIPE)
(id_output, err) = proc.communicate()

# Проверка идентификаторов на уникальность
print('=> Проверка идентификаторов на уникальность.')
ids_file = open('ids.txt')
ids_list = ids_file.read().splitlines()
uniq_ids = [i for i in id_output.split() if not i in ids_list]

# Записать уникальные идентификаторы в файл ids.txt
print('=> Записываются уникальные идентификаторы в файл ids.txt')
uniq_ids_to_ids_file = open('ids.txt', 'a')
uniq_ids_to_ids_file.write('\n'.join(uniq_ids))
uniq_ids_to_ids_file.close()

gen_mail_file = open('mail.txt', 'w')
for len_uniq_ids in range(len(uniq_ids)):
    # Просмотр контента письма по идентификатору
    print('=> Просмотр контента письма по идентификатору.')
    email_content = "ssh USERNAME@mail \"sudo /opt/zimbra/bin/zmmailbox -z -m sony_acc@DOMAIN gm %s\"" % uniq_ids[len_uniq_ids]
    proc = subprocess.Popen(email_content, shell=True, stdout=subprocess.PIPE)
    (content_output, err) = proc.communicate()

    gen_mail_file.writelines(content_output)
gen_mail_file.close()

mail_str = open('mail.txt').readlines()
date_file = open('date.list.diap', 'w')
network_file = open('network.list', 'w')
for line in mail_str:
    if "Account Takeover Attempts" in line:
	begin_datetime = " ".join(line.replace(",", "").split()[:2])
	end_datetime = " ".join(line.replace(",", "").split()[3:5])
	ip = " ".join(line.replace(",", "").split()[6:7])

	new_begin_datetime = datetime.strptime(begin_datetime, "%Y-%m-%d %H:%M")
	new_begin_datetime += timedelta(hours=3)
	new_begin_datetime = new_begin_datetime.strftime("%d.%m.%Y %H:%M:%S")

	new_end_datetime = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M")
	new_end_datetime += timedelta(hours=3)
	new_end_datetime = new_end_datetime.strftime("%d.%m.%Y %H:%M:%S")

	result_datetime = str(new_begin_datetime) + '-' + str(new_end_datetime)
	date_file.writelines("%s\n" % result_datetime)

	if bool([i for i in NATS_LIST if i in ip]):
	    find_nat_ips = "ssh USERNAME@nagioshome \"sudo grep -B3 -R \"%s\$\" /tftp/conf/nat/config.boot-nat*2017* | grep 'address ' | awk '{print \$3}' | sort | uniq | grep \"/\"\"" % ip
	    proc = subprocess.Popen(find_nat_ips, shell=True, stdout=subprocess.PIPE)
	    (output, err) = proc.communicate()
	    network_file.writelines("%s" % output)
	else:
	    print "%s -> It is NOT NAT IP address." % ip
print('=> Generating date.list.diap file.')
date_file.close()
print('=> Generating network.list file.')
network_file.close()

print('=> Очищается файл network.list')
clear_network_file = "ssh USERNAME@details \"sudo cat /dev/null > /home/rss/search/network.list\""
clear_network_file = subprocess.Popen(clear_network_file, shell=True, stdout=subprocess.PIPE)
clear_network_file.wait()

print('=> Очищается файл date.list.diap')
clear_date_file = "ssh USERNAME@details \"sudo cat /dev/null > /home/rss/search/date.list.diap\""
clear_date_file = subprocess.Popen(clear_date_file, shell=True, stdout=subprocess.PIPE)
clear_date_file.wait()

print('=> Удаляются старые файлы TRAF_*')
del_TRAF_files = "ssh USERNAME@details \"sudo rm /home/rss/search/TRAF_*\""
del_TRAF_files = subprocess.Popen(del_TRAF_files, shell=True, stdout=subprocess.PIPE)
del_TRAF_files.wait()

print('=> Пересылается файл network.list')
scp_network_file = subprocess.Popen(["scp", "network.list", "USERNAME@details:/home/rss/search"])
scp_network_file.wait()

print('=> Пересылается файл date.list.diap')
scp_date_file = subprocess.Popen(["scp", "date.list.diap", "USERNAME@details:/home/rss/search"])
scp_date_file.wait()

print('=> Запускается скрипт ./search_diap')
search_diap_run = "ssh USERNAME@details \"sudo /home/rss/search/search_diap\""
search_diap_run = subprocess.Popen(search_diap_run, shell=True, stdout=subprocess.PIPE)
search_diap_run.wait()

print("=> Grep'ается деталька")
grep_for_counts = "ssh USERNAME@details \"grep '104.122.241.225\|104.122.255.22\|104.122.243.148\|104.122.251.148\|104.76.54.68\|104.122.249.104\|172.227.98.188\|184.50.163.183\|2.17.213.103\|2.17.227.183\|23.0.41.158\|23.37.49.18\|23.38.40.215\|23.54.7.44\|23.63.212.105\|88.221.71.62\|88.221.9.29\|23.61.209.168\|23.61.228.129\|23.61.211.183\|23.61.227.212\|23.61.211.183' /home/rss/search/TRAF_* | cut -f 7 -d ' ' | sort | uniq -c | sort -nr\""
grep_for_counts = subprocess.Popen(grep_for_counts, shell=True, stdout=subprocess.PIPE)
grep_for_counts.wait()
(grep_for_counts_output, err) = grep_for_counts.communicate()

grep_for_counts_output = grep_for_counts_output.strip()
data_for_mail = ''
for line in grep_for_counts_output.split('\n'):
    line = line.strip()
    line = line.split()
    if int(line[0]) >= 10:
        grep_ip = "ssh USERNAME@details \"grep '104.122.241.225\|104.122.255.22\|104.122.243.148\|104.122.251.148\|104.76.54.68\|104.122.249.104\|172.227.98.188\|184.50.163.183\|2.17.213.103\|2.17.227.183\|23.0.41.158\|23.37.49.18\|23.38.40.215\|23.54.7.44\|23.63.212.105\|88.221.71.62\|88.221.9.29\|23.61.209.168\|23.61.228.129\|23.61.211.183\|23.61.227.212\|23.61.211.183' /home/rss/search/TRAF_* | grep '%s' | head -5\"" % line[1]
        grep_ip = subprocess.Popen(grep_ip, shell=True, stdout=subprocess.PIPE)
        grep_ip.wait()
	(grep_ip_output, err) = grep_ip.communicate()
	print("IP: %s\nlogin: \n\n%s...") % (line[1], grep_ip_output)
	data_for_mail += "\n\nIP: %s\nlogin: \n\n%s..." % (line[1], grep_ip_output)
    else:
	print('NO grep command for %s' % line[1])

fromaddr = 'Sony <sony_acc@DOMAIN>'
toaddr = 'Levin <USERNAME@DOMAIN>'
subj = 'Sony Abuse'
msg_txt = 'Добрый день.\nС указанных IP-адресов зафиксированы множественные запросы на сервера Sony. %s' % data_for_mail
msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( fromaddr, toaddr, subj, msg_txt)
username = 'sony_acc'
password = ''
server = smtplib.SMTP('mail.DOMAIN:25')
server.set_debuglevel(1)
server.starttls()
server.login(username, password)
server.sendmail(fromaddr, toaddr, msg)
server.quit()
