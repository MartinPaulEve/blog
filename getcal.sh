#! /bin/bash
. /usr/share/virtualenvwrapper/virtualenvwrapper.sh 2> /dev/null
. /usr/local/bin/virtualenvwrapper.sh 2> /dev/null
workon BBKCal
cd /home/martin/Documents/Programming/BBKCal
python3 ./BBKCalImport.py > ./bbk_cal.ics
cp ./bbk_cal.ics ~/Documents/Programming/blog/

