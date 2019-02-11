import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.environ['DATABASE_URL']) # database engine object from SQLAlchemy that manages connections to the database
                                                   # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))     # create a 'scoped session' that ensures different users' interactions with the   
                                                   # database are kept separate


db.execute("TRUNCATE books")

csvFile = open('C:/Users/Spenser/Documents/Online courses/CS50 Web Programming/project1/books.csv')
csvReader = csv.reader(csvFile)
next(csvReader, None)

for row in csvReader:
    for i in range(3):
        row[i] = row[i].replace("'","")
    db.execute(f"INSERT INTO books (isbn, title, author, year) VALUES ('{row[0]}', '{row[1]}', '{row[2]}', {row[3]})")

db.commit()




