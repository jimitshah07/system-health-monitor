# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 12:20:39 2026

@author: Jimit Shah
"""

import psutil
"""
cpu_usage=psutil.cpu_percent(interval=1)
print(f"CPU USAGE: {cpu_usage}%")

memory=psutil.virtual_memory()
print(f"\nMemory Usage: {memory.percent}%")
print(f"Availabe: {memory.available/(1024**3):.2f} GB")
print(f"Totol: {memory.total/(1024**3):.2f} GB")

disk=psutil.disk_usage('C:\\')
print(f"\nDisk Usage: {disk.percent}%")
print(f"Free : {disk.free / (1024**3):.2f} GB")
print(f"Total : {disk.total/(1024**3):.2f}GB")

net=psutil.net_io_counters()
print(f"\nBytes Sent: {net.bytes_sent / (1024**2):.2f} MB")
print(f"Bytes recieved: {net.bytes_recv / (1024**2):.2f} MB")
"""


import psutil
from datetime import datetime, timezone

def get_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')
    net = psutil.net_io_counters()

    stats = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cpu_percent': cpu,
        'memory_percent': memory.percent,
        'memory_available_gb': round(memory.available / (1024**3), 2),
        'memory_total_gb': round(memory.total / (1024**3), 2),
        'disk_percent': disk.percent,
        'disk_free_gb': round(disk.free / (1024**3), 2),
        'disk_total_gb': round(disk.total / (1024**3), 2),
        'net_sent_mb': round(net.bytes_sent / (1024**2), 2),
        'net_recv_mb': round(net.bytes_recv / (1024**2), 2),
    }
    return stats








import os
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, 'system_health_log.csv')

def log_to_csv(stats):
    file_exists=os.path.isfile(CSV_FILE)
    with open(CSV_FILE,mode= "a", newline='') as f:
        writer=csv.DictWriter(f, fieldnames=stats.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(stats)
        

import time

def run_monitor(interval_seconds=2):
    print(f"Starting monitor- logging every {interval_seconds}s. Stop with the red square button in Spyder.")
    while True:
        try:
            stats=get_system_stats()
            log_to_csv(stats)
            print(f"[{stats['timestamp']}] CPU {stats['cpu_percent']}% | Mem {stats['memory_percent']}% | Disk {stats['disk_percent']}%")
        except PermissionError:
            print("CSV is locked (probably open in Excel) — skipped this reading, will retry next cycle.")
        except Exception as e:
            print(f"unexpected exception: {e}")
            
        time.sleep(interval_seconds)
        
        
from collections import deque

def check_alert_condition(threshold=85,consecutive_readings=2):
    if not os.path.isfile(CSV_FILE):
        return False,"No file to log"
    
    with open(CSV_FILE,mode="r") as f:
        reader=csv.DictReader(f)
        last_rows=deque(reader,maxlen=consecutive_readings)
    
    if len(last_rows)< consecutive_readings:
        return False,"Not enough history yet"
    
    cpu_values=[float(row['cpu_percent']) for row in last_rows]
    
    if all(cpu>threshold for cpu in cpu_values):
        return True,f"CPU SUSTAINED ABOVE {threshold}% across last {consecutive_readings} readings : {cpu_values}"
    
    return False,f"CPU ACTING NORMAL :{cpu_values}"

import smtplib
from email.mime.text import MIMEText
def send_email_alert(subject,body):
    sender=os.environ.get('EMAIL_ADDRESS')
    password=os.environ.get('EMAIL_APP_PASSWORD')
    recipient=sender
    
    msg=MIMEText(body)
    msg['SUBJECT']=subject
    msg['From']=sender
    msg['To']=recipient
    
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
        server.login(sender,password)
        server.sendmail(sender,recipient,msg.as_string())
        

"""For Slack"""
import requests

def send_slack_alert(message):
    webhook_url=os.environ.get("SLACK_WEBHOOK_URL")
    payload={"text":message}
    response=requests.post(webhook_url, json=payload)
    return response.status_code




    
if __name__ == "__main__":
    stats = get_system_stats()
    log_to_csv(stats)
    
    
    alert,message=check_alert_condition(threshold=85,consecutive_readings=2)
    if alert:
        print(f"Alert:{message}")
        send_email_alert("System Health alert",message)
        send_slack_alert(message)
    else:
        print(f"OK:{message}")


        




        
