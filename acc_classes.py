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
p = View people list
e = View event list
pa = Add person
ea = Add event
pm = Modify person
em = Modify event
pd = Delete person
ed = Delete event
o = output
q = quit\n:""")
        
            if ans == "pa":
                self.add_person()
            if ans == "ea":
                self.add_event()
            elif ans == "p":
                pass
            elif ans == "e":
                pass
            elif ans == "q":
                sys.exit()






    def add_person(self):
        print "Creating a new person..."
        ok = False
        while not ok:
            name = raw_input("What's their name?   :")
            self.cur.execute("SELECT COUNT(*) FROM people WHERE name=?", (name,))
            tmp = self.cur.fetchone()[0]
            if tmp == 0:
                ok = True
            else:
                print "That name already exists."
        team = raw_input("What team/crew/group are they in?   :")
        note = raw_input("Anything to say about them?   :")
        
        self.cur.execute("INSERT INTO people(name,team,notes) VALUES(?,?,?);", (name,team,note))
        self.con.commit()





    def add_event(self):
        print "Creating an event..."
        ok = False
        while not ok:
            name = raw_input("What was the event?   :")
            self.cur.execute("SELECT COUNT(*) FROM events WHERE name=?", (name,))
            tmp = self.cur.fetchone()[0]
            if tmp == 0:
                ok = True
            else:
                print "That event already exists."
        date = raw_input("What was the date?   :")
        cost = raw_input("How much did it cost?   :\xA3")
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

        

        


