
Why to use incognito window
https://discussions.udacity.com/t/cannot-disconnect-gdisconnect-route/16263/18

# Quotes Catalog

### Project Overview
> To Develop an application that provides a list of items with various categories as well as provide a user registration and authentication system. Registered users have the ability to add, update or delete their items.


### About my implementation
> Keeping the project statement in mind, I have implemented a database of Quotes from various TV shows. The TV shows are added in the database as `Source` and the Quotes are added as, well, `Quotes`. A visitor can look at any quote in the database but to edit the quote or a source require a login. Once logged in, the user can add new sources or quotes or update/delete the ones added by them. 

### Things learnt
    * Development of RESTful web applications using Flask micro-framework
    * Implementing third-party OAuth Authentication to ensure a secure system.
    * Implementing CRUD operations using SQLAlchemy in python.
    
### How to Run?

##### Prerequisites
* Python 2.7
* Vagrant
* Virtual Box

##### Setup Project:
1. Install [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
2. Download the udacity VM files [here](https://d17h27t6h515a5.cloudfront.net/topher/2017/May/59125904_fsnd-virtual-machine/fsnd-virtual-machine.zip) and set up vagrant using `vagrant up` command in the vagrant directory
3. Put the Project folder inside vagrant folder in your local computer

##### Start the project:
1. Launch Vagrant with `vagrant up` if it is not already running
2. Log into VM using SSH, `vagrant ssh`
3. In the SSH prompt, go to `/vagrant/path/to/project`.
4. <em>(Optional)</em>
    Set up the initial Database with some initial data
    ```
        $ python database_setup.py
        $ python populate_db.py
    ```
5. Start the Local Server
    ```
        $ python catalog.py
    ```
6. Access the web app in your browser with the following URL:
    ```
        http://localhost:5000
    ```
    or 
    ```
        http://127.0.0.1:5000
    ```
        
    
###### Notes
> Due to cache handling by browsers, user is sometimes unable to log out. This is a known issue and the workaround is to use the app in incognito/inPrivate Browsing mode or to disable browser Cookie and Cache. Details [from Udacity forums](
https://discussions.udacity.com/t/cannot-disconnect-gdisconnect-route/16263/18)

> Depending on the version of Flask used, one may or may not be able to store credentials object in the `login_session`. This has been mentioned in the `Authentication and Authorization` Course. Make sure the version of Flask in the local machine matches the ones targetted by the project using the following commands:
```
    pip install werkzeug==0.8.3
    pip install flask==0.9
    pip install Flask-Login==0.1.3
```
