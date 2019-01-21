Setting up

create a download folder and fill it with all the data from:
http://trin-hosts.trin.cam.ac.uk/clock/data/2008/
...
http://trin-hosts.trin.cam.ac.uk/clock/data/2019/

on linux you can use: wget -r http://trin-hosts.trin.cam.ac.uk/clock/data/2008/
...

Needs to be done:
- increase efficiency for long term, methods explained here:
http://faculty.franklin.uga.edu/amandal/sites/faculty.franklin.uga.edu.amandal/files/Effective_Statistical_Methods_for_Big_Data_Analytics.pdf
- deal with the fact that not all data is always available (currently such data points are ignored)