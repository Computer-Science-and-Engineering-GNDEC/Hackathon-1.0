<div align="center">
    <img src="https://raw.githubusercontent.com/frappe/erpnext/develop/erpnext/public/images/erpnext-logo.png" height="128">
    <h2>ERPNext</h2>
    <p align="center">
        <p>ERP made simple</p>
    </p>

[https://erpnext.com](https://erpnext.com)

</div>

# Start-up Management Software:

## Software to manage accounts / work of service startup (to be unicorn)

ERPNext requires MariaDB.

ERPNext is built on the [Frappe Framework](https://github.com/frappe/frappe), a full-stack web app framework built with Python & JavaScript.

- [User Guide](https://erpnext.com/docs/user)
- [User Manual for Service Sector](https://docs.erpnext.com/docs/user/manual/en/selling/articles/erpnext-for-services-organization)
- [Video Tutorial](https://docs.erpnext.com/docs/user/videos/learn/services)
- [Discussion Forum](https://discuss.erpnext.com/)

---

## Install an ERPNext Stack on Ubuntu 20.04

## Prerequisites:
  One Ubuntu 20.04 server with at least 4 GB of RAM and a non-root sudo user. </br>
  We set up our server and user by following 
  [Ubuntu 20.04 initial server setup guide](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04).






## Step 1 — Configuring the Firewall

To open multiple ports at once we used the following command:

    sudo ufw allow 22,25,143,80,443,3306,8000/tcp

Alternatively, to allow connections from specific IP addresses on specific ports used this command:

    sudo ufw allow from server_IP to any port port_number

After opening all necessary ports enabled the firewall:

    sudo ufw enable

Then confirmed the status of your firewall:

    sudo ufw status
    
UFW gave an output a list of your enabled rules:

Output
Status: active
<pre>
To                         Action      From
--                         ------      ----
22,25,80,143,443,3306,8000/tcp  ALLOW       Anywhere</br>
OpenSSH                         Allow       Anywhere </br>
22                              Allow       180.188.241.7 </br>
22,25,80,143,443,3306,8000/tcp (v6) ALLOW       Anywhere (v6) </br>
</pre>

## Step 2 — Configuring Locales

First, updated our server:

    sudo apt update

Then configure keymap, language, and character encoding:

    sudo localectl set-keymap us && sudo localectl set-locale LANG=en_US.utf8

Then added the following lines to /etc/environment file.

    sudo nano /etc/environment

Add the following content:</br>
/etc/environment</br></br>
  
    LC_ALL=en_US.UTF-8
    LC_CTYPE=en_US.UTF-8
    LANG=en_US.UTF-8</br

Save and close the file.

Rebooted our server to apply all changes:

    sudo reboot

## Step 3 — Installing MariaDB

    sudo apt install mariadb-server
    
After installing mariadb-server, install the following packages:

    sudo apt install python3-mysqldb libmysqlclient-dev

ERPNext 12 is a Python application and thus it requires the python3-mysqldb library for database management. libmysqlclient-dev is required to access certain MariaDB developer features.

Next, added an extra layer of security to the MariaDB server by running the mysql_secure_installation script:

    sudo mysql_secure_installation
    
The mysql_secure_installation script will prompted us with several questions:

    The first prompt asked about the root password, but since there is no password configured yet, pressed ENTER.
    Next, when asked about changing the MariaDB root password, answer N. Using the default password along with Unix authentication is the recommended setup for Ubuntu-based systems because the root account is closely related to automated system maintenance tasks.
    The remaining questions have to do with removing the anonymous database user, restricting the root account to log in remotely on localhost, removing the test database, and reloading privilege tables. It is safe to answer Y to all those questions.

After completing the mysql_secure_installation script, created a MariaDB Super Admin User

Open up the MariaDB prompt:

    sudo mysql

 Then created a new database named 'hack':
 
    CREATE DATABASE hack;

Confirm that the database was created using this SQL statement:

    SHOW DATABASES;

You will see an output similar to this:
<pre>
Output
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| hack               |
+--------------------+
</pre>

Then created the MariaDB user 'hack' with privileges similar to root and then gave the user a strong password.

    GRANT ALL PRIVILEGES ON *.* TO 'sammy'@'%' IDENTIFIED BY 'mariadb_password' WITH GRANT OPTION;

Then confirm both the user creation and the new user’s privileges:

    SELECT host, user, Super_priv FROM mysql.user;
```
<pre>

    Output should be this:
+-----------+-------+------------+
| Host      | User  | Super_priv |
+-----------+-------+------------+
| localhost | root  | Y          |
| localhost | mysql | Y          |
| %         | hack| Y         |
+-----------+-------+------------+

    3 rows in set (0.001 sec)


    But we are getting this:
+-----------+-------+------------+
| Host      | User  | Super_priv |
+-----------+-------+------------+
| localhost | root  | Y          |
| %         | hack| Y         |
+-----------+-------+------------+

    2 rows in set (0.001 sec)
</pre> 
```
</br>

Then flush privileges to apply all changes:

    FLUSH PRIVILEGES;

Then exit the session:

    exit
    
</br>

# Step 4 — Configuring MariaDB for ERPNext

First, stop mariadb.service:

    sudo systemctl stop mariadb

Now use nano or your favorite text editor to create a MariaDB configuration file called mariadb.cnf:

    sudo nano /etc/mysql/mariadb.conf.d/mariadb.cnf

``` 
<pre>

Now add ERPNext’s official configuration template:
/etc/mysql/mariadb.conf.d/mariadb.cnf

[mysqld]

# GENERAL #
user                           = mysql
default-storage-engine         = InnoDB
socket                         = /var/lib/mysql/mysql.sock
pid-file                       = /var/lib/mysql/mysql.pid

# MyISAM #
key-buffer-size                = 32M
myisam-recover                 = FORCE,BACKUP

# SAFETY #
max-allowed-packet             = 256M
max-connect-errors             = 1000000
innodb                         = FORCE

# DATA STORAGE #
datadir                        = /var/lib/mysql/

# BINARY LOGGING #
log-bin                        = /var/lib/mysql/mysql-bin
expire-logs-days               = 14
sync-binlog                    = 1

# REPLICATION #
server-id                      = 1

# CACHES AND LIMITS #
tmp-table-size                 = 32M
max-heap-table-size            = 32M
query-cache-type               = 0
query-cache-size               = 0
max-connections                = 500
thread-cache-size              = 50
open-files-limit               = 65535
table-definition-cache         = 4096
table-open-cache               = 10240

# INNODB #
innodb-flush-method            = O_DIRECT
innodb-log-files-in-group      = 2
innodb-log-file-size           = 512M
innodb-flush-log-at-trx-commit = 1
innodb-file-per-table          = 1
innodb-buffer-pool-size        = 5462M
innodb-file-format             = barracuda
innodb-large-prefix            = 1
collation-server               = utf8mb4_unicode_ci
character-set-server           = utf8mb4
character-set-client-handshake = FALSE
max_allowed_packet             = 256M

# LOGGING #
log-error                      = /var/lib/mysql/mysql-error.log
log-queries-not-using-indexes  = 0
slow-query-log                 = 1
slow-query-log-file            = /var/lib/mysql/mysql-slow.log

# CONNECTIONS #

pid-file        = /var/run/mysqld/mysqld.pid
socket          = /var/run/mysqld/mysqld.sock
bind-address    = 0.0.0.0

[mysql]
default-character-set = utf8mb4

[mysqldump]
max_allowed_packet=256M
</pre>
```
Save and close the file.

Start mariadb.service:

    sudo systemctl start mariadb

To test the connection you can use the following command. Remember to replace sammy and mariadb_password with your credentials:

    mysql --user hack --password 'mariadb_password' --host=localhost --protocol=tcp --port=3306 test

You will see an output showing MariaDB’s basic help content and several parameters. This means your connection was successful:


Output
mysql  Ver 15.1 Distrib 10.4.13-MariaDB, for debian-linux-gnu (x86_64) using readline 5.2
Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Usage: mysql [OPTIONS] [database]

Default options are read from the following files in the given order:
/etc/my.cnf /etc/mysql/my.cnf ~/.my.cnf
```
...

  --ssl-verify-server-cert
                      Verify server's "Common Name" in its cert against
                      hostname used when connecting. This option is disabled by
                      default.
  -t, --table         Output in table format.
  --tee=name          Append everything into outfile. See interactive help (\h)
                      also. Does not work in batch mode. Disable with
                      --disable-tee. This option is disabled by default.
  -u, --user=name     User for login if not current user.
  -U, --safe-updates  Only allow UPDATE and DELETE that uses keys.
  -U, --i-am-a-dummy  Synonym for option --safe-updates, -U.
  -v, --verbose       Write more. (-v -v -v gives the table output format).

...

max-join-size                     1000000
secure-auth                       FALSE
show-warnings                     FALSE
plugin-dir                        (No default value)
default-auth                      (No default value)
binary-mode                       FALSE
connect-expired-password          FALSE
```


Remember to reload the service using the following command:

    sudo systemctl restart mariadb

Once done, enable MariaDB:

    sudo systemctl enable mariadb

Now that you have tested the database connection, you can continue with the installation of your ERPNext application.

## Step 5 — Setting Up ERPNext 12

Start by preparing the server with all the system packages required by ERPNext 12. Install system-wide dependencies using the following command:

    sudo DEBIAN_FRONTEND=noninteractive apt install -y curl build-essential python3-testresources python3-setuptools python3-dev libffi-dev python3-pip libcurl4 dnsmasq fontconfig git htop libcrypto++-dev libfreetype6-dev liblcms2-dev libwebp-dev libxext6 libxrender1 libxslt1-dev libxslt1.1 libffi-dev ntpdate postfix python3-dev python-tk screen vim 
    xfonts-75dpi xfonts-base zlib1g-dev apt-transport-https libsasl2-dev libldap2-dev libcups2-dev pv libjpeg8-dev libtiff5-dev tcl8.6-dev tk8.6-dev libdate-manip-perl logwatch

Next, update pip3, which is Python’s standard package manager, and then install the latest versions of three additional Python modules:

     sudo -H python3 -m pip install --upgrade setuptools cryptography psutil


setuptools facilitates the installation and upgrading of Python packages, cryptography adds encryption capabilities to your stack, and psutil aids with system monitoring. Now that you have installed all necessary global dependencies, you will now install all the services and libraries required by ERPNext 12.
Setting Up Node.js and Yarn

ERPNext 12 can work with version 8+ of the Node.js server environment. In fact, at the time of this writing, the official ERPNext easy_install script uses Node 8. But from a security perspective, it’s advisable to install a newer version because Node 8 reached its End Of Life (EOL) in 2020 and thus will not receive any more security patches. At the time of this writing, Ubuntu 20.04 contains version 10.19 of Node.js. Although this version is still maintained, for similar reasons (EOL in less than a year) it’s highly advisable to avoid using it. For this guide, Node.js version 12 LTS will be installed along with the corresponding npm and yarn package managers. Please note that the Frappe framework uses yarn to install dependencies. If you decide to use an alternative installation method then make sure that you end up with version 1.12+ of yarn running in your system.

Add the NodeSource repository to your system:

    curl -sL https://deb.nodesource.com/setup_12.x -o nodesource_setup.sh

 

Now you can inspect the contents of the downloaded script:

    sudo nano nodesurce_setup.sh

 

Once you are satisfied with the script’s contents you can run the script:

    sudo bash nodesource_setup.sh

 

This script will automatically update the apt list. Now you can install nodejs on your server:

    sudo apt install nodejs

 

Next, install yarn globally using the npm package manager:

    sudo npm install -g yarn

 

Now that you have installed Node you can continue to configure wkhtmltopdf for your platform.

ERPNext uses the wkhtmltopdf open source tool to convert HTML content into PDF using the Qt WebKit rendering engine. </br>
This feature is mostly used for printing invoices, quotations, and other reports. In the case of ERPNext 12, a specific version of wkhtmltopdf is required, 0.12.5 with patched Qt.

To install wkhtmltopdf, start by switching to a suitable directory to download the package, in this case /tmp:

    cd /tmp

 

Download the appropriate wkhtmltopdf version and package for Ubuntu 20.04 from the project’s page:

    wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb

 

Now install the package using the dpkg tool:

    sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb

 

Next, copy all relevant executables to your /usr/bin/ directory:

    sudo cp /usr/local/bin/wkhtmlto* /usr/bin/

 

Once the files are in place, change their permissions to make them executable:

    sudo chmod a+x /usr/bin/wk*

 

Now that wkhtmltopdf is properly installed we will add Redis to our database stack.
Installing Redis

ERPNext 12 uses Redis to enhance MariaDB’s performance. Specifically, Redis assists with caching.

First, install Redis from the official Ubuntu 20.04 repository:

    sudo apt install redis-server

 

Then enable Redis on startup:

    sudo systemctl enable redis-server

 

Now that you have added Redis to your stack let’s take a moment to summarize what you have accomplished so far. Up to this point, you have installed all the major components required by ERPNext 12, which include:

    A MariaDB database backend
    The Node.js JavaScript server environment
    The Yarn package manager
    A Redis database cache
    The wkhtmltopdf PDF documents generator

Whether you are installing the ERP system for development or for production, you are now ready for the next step, which is installing the Frappe full-stack framework and the actual ERPNext 12 web application.

## Step 6 — Installing Frappe Bench CLI

Now that you have installed all of ERPNext’s stack requirements you can unleash the flexibility of Frappe’s bench command-line utility. </br>
The bench CLI was designed with the purpose of assisting users in the process of installing, setting up, and managing applications </br>
like ERPNext that are based on the Frappe Framework. In the coming sections, you will install the bench CLI and then use it to complete the process of setting up ERPNext 12.</br>

Make sure that the Frappe user (in this case sammy) has the proper rights on its home directory:

    sudo chown hack -R /home/hack

 

Now clone the frappe/bench repository to your home directory. Remember to replace sammy with your system username:

    git clone https://github.com/frappe/bench /home/hack/.bench --depth 1 --branch master

 

Install the bench CLI:

    sudo pip3 install -e /home/hack/.bench

 
