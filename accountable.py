#!/usr/bin/python
# -*- coding: utf-8 -*-

# TABLES TO ADD
# payments
# driving

# THINGS TO ADD
# The Club
# Who paid for an event
# Parsing
# Rounding errors

# QUESTIONS
# How is best to parse the date input?
# 

import sqlite3 as lite
import sys
import math

class DatabaseHandler:
    
    def __init__(self, con):
        con.row_factory = lite.Row
        self.con = con
        self.cur = con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS people(
                    idx INTEGER PRIMARY KEY,
                    name TEXT,
                    team TEXT,
                    notes TEXT
                    starting_balance INTEGER
                        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS events(
                    idx INTEGER PRIMARY KEY,
                    name TEXT,
                    date REAL,
                    cost INTEGER,
                    notes TEXT
                        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS p_e(
                    idx INTEGER PRIMARY KEY,
                    person INTEGER,
                    event INTEGER,
                    ratio REAL
                        )""")


    def check_person_exists(self,name):
        self.cur.execute("SELECT COUNT(*) FROM people WHERE name=?", (name,))
        tmp = self.cur.fetchone()[0]
        if tmp == 0:
            exist = False
        else:
            exist = True
        return exist


    def check_event_exists(self,name):
        self.cur.execute("SELECT COUNT(*) FROM events WHERE name=?", (name,))
        tmp = self.cur.fetchone()[0]
        if tmp == 0:
            exist = False
        else:
            exist = True
        return exist


    def insert_person(self, name, team, starting_balance, note):
        self.cur.execute("INSERT INTO people(name,team,starting_balance,notes) VALUES(?,?,?,?);", (name,team,starting_balance,note))
        self.con.commit()
        idx = self.cur.lastrowid
        return idx


    def insert_event(self, name, date, cost, note):
        self.cur.execute("INSERT INTO events(name,date,cost,notes) VALUES(?,?,?,?);", (name,date,cost,note))
        self.con.commit()
        idx = self.cur.lastrowid
        return idx


    def delete_person(self, field, match):
        instruct = "SELECT * FROM people WHERE %s=?" % field
        self.cur.execute(instruct, (match,))
        person = self.cur.fetchone()
        idx = person["idx"]
        self.cur.execute("DELETE FROM people WHERE idx=?", (idx,))
        self.cur.execute("DELETE FROM p_e WHERE person=?", (idx,))
        self.con.commit()


    def delete_event(self, field, match):
        instruct = "SELECT * FROM events WHERE %s=?" % field
        self.cur.execute(instruct, (match,))
        event = self.cur.fetchone()
        idx = event["idx"]
        self.cur.execute("DELETE FROM events WHERE idx=?", (idx,))
        self.cur.execute("DELETE FROM p_e WHERE event=?", (idx,))
        self.con.commit()


    def link_people_to_event(self, event_idx, people_idx_list, ratio_list):
        for (pp,rr) in zip(people_idx_list, ratio_list):
            self.cur.execute("INSERT INTO p_e(person, event, ratio) VALUES(?,?,?);", (pp,event_idx,rr))
        self.con.commit()


    def retrieve_people(self, field=None, match=None):
        if field is None:
            self.cur.execute("SELECT * FROM people")
        else:
            instruct = "SELECT * FROM people WHERE %s=?" % field
            self.cur.execute(instruct, (match,))
        people = self.cur.fetchall()
        return people


    def retrieve_events(self, field=None, match=None):
        if field is None:
            self.cur.execute("SELECT * FROM events")
        else:
            instruct = "SELECT * FROM events WHERE %s=?" % field
            self.cur.execute(instruct, (match,))
        events = self.cur.fetchall()
        return events


    def retrieve_events_by_person(self, person_idx):
        self.cur.execute("SELECT * FROM p_e WHERE person=?", (person_idx,))
        link_list = self.cur.fetchall()
        events = []
        shares = []
        for ll in link_list:
            event_idx = ll["event"]
            self.cur.execute("SELECT * FROM events WHERE idx=?",(event_idx,))
            event = self.cur.fetchone()
            ratio_sum = self.event_ratio_sum(event["idx"])
            share = self.calculate_share(event["cost"], ll["ratio"], ratio_sum)
            events.append(event)
            shares.append(share)
        return events,shares


    def retrieve_people_by_event(self, event_idx):
        self.cur.execute("SELECT * FROM p_e WHERE event=?", (event_idx,))
        link_list = self.cur.fetchall()
        people = []
        ratios = []
        for ll in link_list:
            person_idx = ll["person"]
            self.cur.execute("SELECT * FROM people WHERE idx=?",(person_idx,))
            person = self.cur.fetchone()
            people.append(person)
            ratios.append(ll["ratio"])
        return people,ratios


    def balance(self, subject_idx):
        self.cur.execute("SELECT * FROM people WHERE idx=?", (subject_idx,))
        person = self.cur.fetchone()
        starting_balance = person["starting_balance"]
        events,event_shares = self.retrieve_events_by_person(subject_idx)
        balance = starting_balance + math.fsum(event_shares)
        return balance,starting_balance,events,event_shares


    def event_ratio_sum(self, event_idx):
        self.cur.execute("SELECT * FROM p_e WHERE event=?", (event_idx,))
        link_list = self.cur.fetchall()
        ratios = []
        for ll in link_list:
            ratios.append(ll["ratio"])
        ratio_sum = math.fsum(ratios)
        return ratio_sum


    def calculate_share(self, cost, ratio, ratio_sum):
        share = cost*ratio/ratio_sum
        share = math.ceil(share)
        share = -int(share)
        return share




class CmdLineUI:

    def __init__(self, db):
        self.db = db

    def main(self):
        while True:
            ans = raw_input("""What would you like to do?
vp = View people list
ve = View event list
ap = Add person
ae = Add event
dp = Delete person
de = Delete event
sp = Statement for a single person
se = Statement for a single event
q  = quit\n:""")
        
            if ans == "ap":
                self.cb_add_person()
            if ans == "ae":
                self.cb_add_event()
            if ans == "dp":
                self.cb_remove_person()
            if ans == "de":
                self.cb_remove_event()
            if ans == "vp":
                self.cb_view_people()
            if ans == "ve":
                self.cb_view_events()
            if ans == "sp":
                self.cb_person_statement()
            if ans == "se":
                self.cb_event_statement()
            if ans == "q":
                sys.exit()


    ### CALLBACK METHODS ###

    def cb_add_person(self):
        print "Creating a new person..."
        exist = True
        while exist:
            name = raw_input("What's their name?   :")
            if name == "":
                return
            exist = self.db.check_person_exists(name)
            if exist:
                print "   That person already exists."
        team = raw_input("What team/crew/group are they in?   :")
        note = raw_input("Anything to say about them?   :")
        sys.stdout.write(u'What is their opening balance?   :£')
        starting_balance = self.money_parse_in(raw_input(""))
        self.db.insert_person(name, team, starting_balance, note)


    def cb_add_event(self):
        print "Creating an event..."
        exist = True
        while exist:
            name = raw_input("What was the event?   :")
            if name == "":
                return
            exist = self.db.check_event_exists(name)
            if exist:
                print "   That event already exists."
        date = raw_input("What was the date?   :")
        sys.stdout.write(u'How much did it cost?   :£')
        cost = self.money_parse_in(raw_input(""))
        note = raw_input("Any notes?   :")
        event_idx = self.db.insert_event(name,date,cost,note)
        
        # Now get a list of people contributing
        self.display_people()
        tmp = raw_input("Enter a list of ids seperated by spaces for the people who attended this event:")
        people_idx_list = map(int, tmp.split())
        tmp = raw_input("Enter the payment ratios for each person seperated by spaces (so for two people, \"2 1\" means the first person pays twice as much):")
        ratio_list = map(float, tmp.split())
        # THIS NEEDS SOME MORE PARSING TO MAKE SURE THEY'RE VALID, EXISTING IDXS
        self.db.link_people_to_event(event_idx, people_idx_list, ratio_list)


    def cb_remove_person(self):
        self.display_people()
        idx = raw_input("Enter the id of the person you want to remove:")
        self.db.delete_person("idx", idx)


    def cb_remove_event(self):
        self.display_events()
        idx = raw_input("Enter the id of the event you want to remove:")
        self.db.delete_event("idx", idx)


    def cb_view_people(self):
        self.display_people()
        raw_input("Press enter to continue")


    def cb_view_events(self):
        self.display_events()
        raw_input("Press enter to continue")


    def cb_person_statement(self):
        self.display_people()
        idx = raw_input("Enter the id of the person whose statement you want:")
        subject = self.db.retrieve_people('idx', idx)[0]
        subject_idx = subject["idx"]
        print "Retrieving statement for %s." % subject["name"]
        balance,starting_balance,items,shares = self.db.balance(subject_idx)
        print "_______________________________________"
        print u"Starting Balance: £" + self.money_parse_out(starting_balance)
        print "_______________________________________"
        print "id | Name                 | Date       | Cost       | Share      | Notes"
        for ee,ss in zip(items,shares):
            print "%2s | %-20s | %-10s | %-10s | %-10s | %s" % (ee["idx"], ee["name"], ee["date"], self.money_parse_out(ee["cost"]), self.money_parse_out(ss), ee["notes"])
        print "_______________________________________"
        print u"Balance: £" + self.money_parse_out(balance)
        print "_______________________________________"
        raw_input("Press enter to continue")


    def cb_event_statement(self):
        self.display_events()
        idx = raw_input("Enter the id of the event whose details you want:")
        subject = self.db.retrieve_events("idx", idx)[0]
        subject_idx = subject["idx"]
        people,ratios = self.db.retrieve_people_by_event(subject_idx)
        print "_______________________________________"
        print "Event: %s" % subject["name"]
        print "Date:  %s" % subject["date"]
        print u'Cost:  £%s' % self.money_parse_out(subject["cost"])
        print "Notes: %s" % subject["notes"]
        print "The following people participated in this event:"
        for (pp, rr) in zip(people,ratios):
            print "     %2s | %-20s | %-5s " % (pp["idx"], pp["name"], str(rr))
        print "_______________________________________"
        raw_input("Press enter to continue")


    ### DISPLAY METHODS ###
    
    def display_people(self, field=None, match=None):
        people = self.db.retrieve_people(field, match)
        if people is None:
            print("Noone matching")
            return
        print("id | Name                 | Team       | Notes")
        for pp in people:
            print ("%2s | %-20s | %-10s | %s" % (pp["idx"], pp["name"], pp["team"], pp["notes"]))


    def display_events(self, field=None, match=None):
        events = self.db.retrieve_events(field, match)
        if events is None:
            print("No events matching")
            return
        print "id | Name                 | Date       | Cost       | Notes"
        for ee in events:
            print "%2s | %-20s | %-10s | %-10s | %s" % (ee["idx"], ee["name"], ee["date"], self.money_parse_out(ee["cost"]), ee["notes"])


    def money_parse_out(self, money):
        money_str = '%.2f' % (money/100.0)
        return money_str

    def money_parse_in(self, money):
        money_int = int(round(100.0*float(money)))
        return money_int
        






### MAIN CODE ###

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
    db = DatabaseHandler(con)
    ui = CmdLineUI(db)
    ui.main()

sys.exit()

