## RUN as `python3 api.py`

## PRE-REQUISITES
- perf.txt needs to created and kept in the same directory as this
- perf.txt is basically the performance of today's match
- It is created using a socket MITMproxy
- The mimtdump script is to be run like:
- mitmdump -p 8089 -s create_perf_file.py --ssl-insecure
- create_perf_file.py is also checking it in this repo
- Set Firefox browser proxy as 127.0.0.1 with port 8089
- Go to arena.topcoder.com and login and click on any Room, eg. Room5
- The File perf.txt should be created now
- THE perf.txt FILE NEEDS TO BE CREATED AFTER EACH NEW SRM