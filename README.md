# query_sep
query Symantec Endpoint Protection

# SECURITY NOTE:
I wrote the .py file.  You have my word that they don't do anything nefarious.  Even so, I recommend that you perform
your own static analysis and supply chain testing before use.  Many libraries are imported that are not in my own control.

# usage
```
$ python query_sep.py -h
usage: query_sep.py [-h] --hostname HOSTNAME --username USERNAME --password PASSWORD [--domain DOMAIN] [--machine MACHINE] [--proxies PROXIES]

options:
  -h, --help           show this help message and exit
  --hostname HOSTNAME  The host name of your SEP server (my-sep-host.my-domain.com)
  --username USERNAME  The user name for your SEP admin user
  --password PASSWORD  The password for your SEP admin user
  --domain DOMAIN      The domain for your SEP admin user
  --machine MACHINE    machine name to search for
  --proxies PROXIES    JSON structure specifying 'http' and 'https' proxy URLs
```


# example: look up machines
```
python query_sep.py --hostname MySEPHost --username MyUserName --password MyPassword --machine LT-12345
```

# references: 
https://apidocs.securitycloud.symantec.com/#/doc?id=computers
