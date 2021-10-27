#!/bin/bash
PYTHONHTTPSVERIFY=0 python /var/www/cgi-bin/api/daemon-glycan.py
PYTHONHTTPSVERIFY=0 python /var/www/cgi-bin/api/daemon-protein.py
PYTHONHTTPSVERIFY=0 python /var/www/cgi-bin/api/daemon-archive-caches.py
PYTHONHTTPSVERIFY=0 python /var/www/cgi-bin/api/daemon-clear-caches.py
