# Linux Server Configuration

### Project Overview
> A baseline installation of a linux server and preparing it to host our web applications, securing it from a number of attack vectors, installing and configuring a database server and deploying the Item Catalog application onto it.

The server is a free-tier Amazon EC2 instance with a 100% uptime.

* Public IP Address: 35.154.33.179
* To view the live version with Google authentication:
  ```
  Google Does not allow the use of public IP in client ID
  http://35.154.33.179.xip.io
  http://ec2-35-154-33-179.ap-south-1.compute.amazonaws.com

  ```
* Accessible SSH port: 2200

### Requirements

To run this project, you should have the following things on your computer:
* Any browser
* A Stable Internet connection
* Terminal shell for conencting t linux server and configuring it

### How to execute the project

###### Connecting to the server in Terminal
* Paste the content given in the notes in a key.pub file
* use `ssh grader@ip-address -p 2200 -i KEY.pub`

###### Updating the server software
  * `sudo apt-get update`
  * `sudo apt-get upgrade`
  * `sudo apt-get dist-upgrade`

###### Creating the user grader and giving sudo access
  * `sudo adduser grader`
  * `sudo touch /etc/sudoers.d/grader`
  * `sudo nano /etc/sudoer.d/grader`
  * Now, In this file, write and save the following:
  ```
    grader ALL=(ALL) NOPASSWD: ALL
  ```

###### Allow grader to login via public key
  * When connected as root on server, execute the following:
  ```
    # su - grader
    $ sudo mkdir .ssh
    $ sudo nano .ssh/authorized_keys
  ```
  * Copy the contents of the public key generated on the local computer to the authorized_keys file on server
  ```
    $ sudo chmod 700 .ssh
    $ sudo chmod 600 .ssh/authorized_keys
    $ sudo service ssh restart
  ```
  * Now exit SSH and login to grader account's SSH through rsa key using:
  `ssh -i grdr_key grader@ip-address`

###### Disable Root login, Enforce key-based authentication and change SSH port
  * Run `$ sudo nano /etc/ssh/sshd_config`
  * Find **PermitRootLogin** line and edit it to no
  * Find the **PasswordAuthentication** line and edit it to no
  * Find the **Port** line and change `22` to `2200`
  * Restart SSH service using `$ sudo service ssh restart`

Now we can login to the remote VM using
```
  $ ssh -i grdr_key grader@ip-address -p 2200
```

###### Configure local timezone to UTC
  * Change the time to UTC using:
    `$ sudo timedatectl set-timezone UTC`

###### Configure UFW
```
  $ sudo ufw default deny incoming
  $ sudo ufw allow 2200/tcp
  $ sudo ufw allow 80/tcp
  $ sudo ufw allow 123/udp
  $ sudo ufw deny 22/tcp
  $ sudo ufw enable
```

###### install Apache2, mod_wsgi and git
  `$ sudo apt-get install apache2 libapache2-mod-wsgi git`
  * Enable mod_wsgi:
  `$ sudo a2enmod wsgi`

###### Install and Configure PostgreSQL
  * Install the required packages
  ```
    $ sudo apt-get install postgresql postgresql-contrib libpq-dev python-dev
  ```
  * Login as *postgres* User(Default user), and get into psql shell
  ```
  $ sudo su - postgres
  $ psql
  ```
  * Create new User named *catalog*
  `CREATE USER catalog WITH PASSWORD 'password';`
  * Create a new Database *catdb*
  `CREATE DATABASE catdb WITH OWNER catalog;`
  * Connect to the Database
  `\c catdb`
  * Revoke all rights from public, and allow only catalog to perform transactions
  ```
  REVOKE ALL ON SCHEMA public FROM public;
  GRANT ALL ON SCHEMA public TO catalog
  ```

###### Install python app dependencies
```
  $ sudo apt-get install python-pip
  $ sudo pip install Flask=0.9
  $ sudo pip install httplib2 oauth2client sqlalchemy psycopg2 sqlalchemy_utils requests
```

###### Clone the application files
  * Make a *project* directory in /var/www
  * Clone the project files from Git to catalog directory
  `$ git clone https://github.com/the-cybersapien/ND-004-Full-Stack-Udacity.git project`
  * Change the move the Project files from subfolder to project root.
  * Create WSGI file
  ```
  $ touch catalog.wsgi && nano catalog.wsgi
  ```

  ```
  import sys
  import logging
  logging.basicConfig(stream=sys.stderr)
  sys.path.insert(0, "/var/www/project/")

  from catalog import app as application
  application.secret_key = 'MY_SECRET_KEY'
  ```

###### Change the engine inside the .py files to
```
  engine = create_engine('postgresql://catalog:password@lolocalhost/catdb')
```
###### Setup the initial data
```
  $ python database_setup.py
  $ python populate_db.py
```
###### Edit the Virtual File
```
sudo nano /etc/apache2/sites-available/000-default.conf
```
Add the following content to the file:
```
<VirtualHost *:80>
        ServerName 35.154.33.179

        ServerAdmin aditya@cybersapien.xyz
        WSGIScriptAlias / /var/www/project/catalog.wsgi
        <Directory /var/www/project/>
                Order allow,deny
                Allow from all
        </Directory>
        Alias /static /var/www/project/static
        <Directory /var/www/project/static/>
                Order allow,deny
                Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

```

###### Restart Apache to launch
```
  $ sudo service apache2 restart
```

###### references
- Stackoverflow community.<br>
- AWS documentation.<br>
- Flask documentation.<br>
- Python documentation.<br>
- Slack for FSND
- Udacity.
