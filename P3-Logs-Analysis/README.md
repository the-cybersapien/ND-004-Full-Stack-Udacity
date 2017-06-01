# Log Analysis

### Project Overview
> In this project, we work on data that could come from a real-world web application, with fields
>representing information that a web server would record, such as HTTP status codes and URL paths. The web
>server and the reporting tool both connect to the same database, allowing information to flow from the web
>server into the report

### How to Run

##### Pre-requisite
* Python3
* Vagrant
* Virtualbox

##### Setup project
1. Install [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
2. Download the udacity VM files [here](https://d17h27t6h515a5.cloudfront.net/topher/2017/May/59125904_fsnd-virtual-machine/fsnd-virtual-machine.zip) and set up vagrant using `vagrant up` command in the vagrant directory
3. Download the SQL data [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)
4. Unzip and place the sql file inside the vagrant directory

##### Start the project
1. Launch Vagrant with `vagrant up` if it is not alreadyy running.
2. Log into the VM using SSH, `vagrant ssh`
3. In the SSH prompt, go to /vagrant directory
4. Load the sql data to local database using `psql -d news -f newsdata.sql`

#### Database Schema
The Database includes 3 tables by default,
* The `authors` table
* The `articles` table
* The `log` table

Schema for the tables is as follows:
###### Articles Table

| Column         | Type           |
| :-------------:| :-------------:|
| author         | integer        |
| title          | text           |
| slug           | text           |
| lead           | text           |
| body           | text           |
| time           | timestamp with timezone |
| id             | integer (PRIMARY KEY) |


###### Authors Table
| Column         | Type           |
| :------------- | :------------- |
| name           | text           |
| bio            | text           |
| id             | integer (PRIMARY KEY)|


##### Logs table
| Column         | Type           |
| :------------- | :------------- |
| path           | text           |
| ip             | inet           |
| method         | text           |
| status         | text           |
| time           | timestamp      |
| id             | integer(PRIMARY KEY)|


##### The Logs Analysis script
The logs Analysis script is designed in such a way that it checks automatically if the required views are existing in the databse or not. If they are not found, then they are created. This eleminates the additional setup required.
###### Running the project

From the vagrant directory inside the virtual machine, run logs.py in Python3

```
  $ python3 logs.py
```
