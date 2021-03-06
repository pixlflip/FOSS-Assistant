""" Until Database function is immplimented properly this is a command line script to add a user by hand. """
import MySQLdb
from API_Server.Functions import Protocols

# All key (read top level) variables here
SETTINGS = Protocols.Settings()
SQLDATABASE = SETTINGS.sqlDatabase
SQLUSERNAME = SETTINGS.sqlUsername
SQLPASSWORD = SETTINGS.sqlPassword
# End Key Variables =======================

profileParams = []
print("FOSS ASSISTANT ADD PROFILE SCRIPT ")
profileParams.append(input("= Enter your Username: ").lower().replace(' ', ''))
profileParams.append(input("= Enter your Password: "))
profileParams.append(input("= Enter your Email Address: "))
profileParams.append(input("= Enter your Password for Email Above: "))
profileParams.append(input("= Enter Discord ID (put NONE if no ID): "))
# Add user to database
try:
    # open the database
    db = MySQLdb.connect("localhost", SQLUSERNAME, SQLPASSWORD, SQLDATABASE)
    cursor = db.cursor()
    # Execute the SQL command
    sql = "INSERT INTO PROFILES (USER, PASSWORD, EMAIL, EMAILPASS, DISCORD) VALUES (%s, %s, %s, %s, %s)"
    val = (profileParams[0], profileParams[1], profileParams[2], profileParams[3], profileParams[4])
    cursor.execute(sql, val)

    db.commit()

    print(cursor.rowcount, "record inserted.")
except:
    # Rollback in case there is any error
    db.rollback()
    print("An error occurred and the profile was not saved. Make sure you have ran initial setup.")

# disconnect from server
db.close()
# print and end
print("Profile created successfully.")