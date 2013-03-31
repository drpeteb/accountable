#!/usr/bin/python
# -*- coding: utf-8 -*-

# TABLES TO ADD
# payments
# driving

# METHODS TO ADD
# Add event
# Modify person
# Modify event
# Delete person
# Delete event
# View people
# View events
# Generate balance

# QUESTIONS
# How is best to parse the date input?
# 

import sqlite3 as lite
import sys





class Account:
    
    def __init__(self, con):
        self.con = con
        self.cur = con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS people(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    team TEXT,
                    notes TEXT
                    starting_balance REAL
                        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    date REAL,
                    cost REAL,
                    notes TEXT
                        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS p_e(
                    id INTEGER PRIMARY KEY,
                    person INTEGER,
                    event INTEGER,
                    ratio REAL
                        )""")





    def main(self):
        
        while True:
            
            ans = raw_input("""What would you like to do?
vp = View people list
ve = View event list
ap = Add person
ae = Add event
mp = Modify person
me = Modify event
dp = Delete person
de = Delete event
s  = Statement
q  = quit\n:""")
        
            if ans == "ap":
                self.ui_add_person()
            if ans == "ae":
                self.ui_add_event()
            if ans == "vp":
                self.ui_view_people()
            if ans == "ve":
                self.ui_view_events()
            if ans == "s":
                self.ui_statement()
            if ans == "q":
                sys.exit()






    def ui_add_person(self):
        print "Creating a new person..."
        exist = True
        while exist:
            name = raw_input("What's their name?   :")
            exist = self.db_check_person_exists(name)
            if exist:
                print "   That person already exists."
        team = raw_input("What team/crew/group are they in?   :")
        note = raw_input("Anything to say about them?   :")
        
        self.cur.execute("INSERT INTO people(name,team,notes) VALUES(?,?,?);", (name,team,note))
        self.con.commit()





    def ui_add_event(self):
        print "Creating an event..."
        exist = True
        while exist:
            name = raw_input("What was the event?   :")
            exist = self.db_check_event_exists(name)
            if exist:
                print "That event already exists."
        date = raw_input("What was the date?   :")
        sys.stdout.write(u'How much did it cost?   :£')
        cost = raw_input("")
        note = raw_input("Any notes?   :")
        
        self.cur.execute("INSERT INTO events(name,date,cost,notes) VALUES(?,?,?,?);", (name,date,cost,note))
        event_id = self.cur.lastrowid
        
        # Display the possible people
        self.cur.execute("SELECT * FROM people")
        rows = self.cur.fetchall()
        for rr in rows:
            print "%s %s" % (rr["id"], rr["name"])

        tmp = raw_input("Enter a list of ids seperated by spaces for the people who attended this event:")
        id_list = map(int, tmp.split())

        for pp in id_list:
            self.cur.execute("INSERT INTO p_e(person, event) VALUES(?,?);", (pp,event_id))
            # THIS NEEDS SOME PARSING TO MAKE SURE THEY'RE VALID, EXISTING IDS

        self.con.commit()

        

        

    def ui_view_people(self):
        self.display_people()
        raw_input("Press enter to continue")





    def ui_view_events(self):
        self.display_events()
        raw_input("Press enter to continue")





    def ui_statement(self):
        self.display_people()
        id = raw_input("Enter the id of the person whose statement you want:")
        self.cur.execute("SELECT * FROM people WHERE id=?",id)
        subject = self.cur.fetchone()
        print "Retrieving statement for %s." % subject["name"]
        self.cur.execute("SELECT * FROM p_e WHERE person=?",id)
        e_list = self.cur.fetchall()
        print "id | Name                 | Date       | Cost       | Notes"
        for ee in e_list:
            e_id = ee["event"]
            self.cur.execute("SELECT * FROM events WHERE id=?",(e_id,))
            event = self.cur.fetchone()
            print "%2s | %-20s | %-10s | %-10s | %s" % (event["id"], event["name"], event["date"], event["cost"], event["notes"])
        raw_input("Press enter to continue")
        



    ### DATABASE METHODS ###

    def db_check_person_exists(self,name):
        self.cur.execute("SELECT COUNT(*) FROM people WHERE name=?", (name,))
        tmp = self.cur.fetchone()[0]
        if tmp == 0:
            exist = False
        else:
            exist = True
        return exist

    def db_check_event_exists(self,name):
        self.cur.execute("SELECT COUNT(*) FROM events WHERE name=?", (name,))
        tmp = self.cur.fetchone()[0]
        if tmp == 0:
            exist = False
        else:
            exist = True
        return exist
        

    ### DISPLAY METHODS ###
    
    def display_people(self):
        # Display a list of everyone in the database
        print "Here's a list of everyone in the database"
        self.cur.execute("SELECT * FROM people")
        rows = self.cur.fetchall()
        print "id | Name                 | Team      | Notes"
        for rr in rows:
            print "%2s | %-20s | %-10s | %s" % (rr["id"], rr["name"], rr["team"], rr["notes"])





    def display_events(self):
        # Display a list of all the events
        print "Here's a list of all the events in the database"
        self.cur.execute("SELECT * FROM events")
        rows = self.cur.fetchall()
        print "id | Name                 | Date       | Cost       | Notes"
        for rr in rows:
            print "%2s | %-20s | %-10s | %-10s | %s" % (rr["id"], rr["name"], rr["date"], rr["cost"], rr["notes"])









# See if we got an argument
if len(sys.argv) == 1:

    # No argument. Create a database?
    filename = raw_input("Enter the name of your database (If it doesn't exist, it will be created.):")

    if filename == "":
        sys.exit()
    elif filename[-3:] != ".db":
        filename = filename + ".db"

else:

    # We have an argument.
    filename = sys.argv[1]

con = lite.connect(filename)
with con:
    con.row_factory = lite.Row
    cur = con.cursor()
    acc = Account(con)
    acc.main()

sys.exit()

