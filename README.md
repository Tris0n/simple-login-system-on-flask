# simple login system on flask

RUN COMMANDS:
```
sudo apt-get update -y
sudo apt-get install -y python3-mysqldb
sudo apt install mysql-server -y
sudo mysql -u root -p
CREATE USER 'user'@'localhost' IDENTIFIED BY '';


export SECRET_KEY=str0ng_p4ss0wrd_f0r_y0ur_s3curity
pip3 install -r requirements.txt

in python3 console:
python3
from app import db
db.create_all()
exit()


python3 app.py
```
----------------------------------------------------

uncomment line 168 to start the server
access in you browser -> http://127.0.0.1:5000/
