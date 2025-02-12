# Arshadullah Khan 2/8/25
# CS 341 - Project 1 – Chicago Traffic Camera Analysis
#
# The goal of this project is to write a console-based Python program that inputs commands from the
# user and outputs data from the Chicago traffic camera database. SQL should be used to retrieve and
# compute most of the information, while Python is used to display the results and, if the user chooses,
# to plot figures as well.

import sqlite3
import matplotlib.pyplot as plt
import datetime

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")

    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")

    dbCursor.execute("SELECT COUNT(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Camera Violation Entries:", f"{row[0]:,}")

    dbCursor.execute("SELECT COUNT(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Speed Camera Violation Entries:", f"{row[0]:,}")

    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM RedViolations;")
    row = dbCursor.fetchone()
    print(f"  Range of Dates in the Database: {row[0]} - {row[1]}")

    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")

    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")

################################################################## 
#
# check_Exists
#
# Given a connection to the database, checks to see if a value exists
# in a specific column of table

def check_Exists(dbConn, table, key, value):
    dbCursor = dbConn.cursor()
    dbCursor.execute(f"Select Exists(Select 1 From {table} Where {key} = ? LIMIT 1)", (value,))
    result = dbCursor.fetchone()[0]
    return bool(result)


##################################################################  
#
# print_intersections
#
# Given a connection to the database and name of intersection, searches
# and returns intersections with their IDs that matches the search


def print_intersections(dbConn, search):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT Intersection_ID, Intersection FROM Intersections WHERE Intersection LIKE ? ORDER BY Intersection ASC", (search,))
    intersections = dbCursor.fetchall()

    if len(intersections) == 0:
        print("No intersections matching that name were found.")
    else:
        for row in intersections:
            print(f"{row[0]} : {row[1]}")
    print()

##################################################################  

#
# find_Cameras
#
# Given a connection to the database and an intersection, returns all red Light Cameras and Speed Cameras
#


def find_Cameras(dbConn, search):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT c.Camera_ID, c.Address FROM RedCameras c JOIN Intersections i on c.Intersection_ID = i.Intersection_ID WHERE i.Intersection = ? ORDER BY c.Camera_ID ASC", (search,))
    redCams = dbCursor.fetchall()

    print()
    if len(redCams) == 0:
        print("No red light cameras found at that intersection.")
    else:
        print("Red Light Cameras:")
        for row in redCams:
            print(f"  {row[0]} : {row[1]}")
    print()
    dbCursor.execute("SELECT c.Camera_ID, c.Address FROM SpeedCameras c JOIN Intersections i on c.Intersection_ID = i.Intersection_ID WHERE i.Intersection = ? ORDER BY c.Camera_ID ASC", (search,))
    speedCams = dbCursor.fetchall()
    if len(speedCams) == 0:
        print("No speed cameras found at that intersection.")
    else:
        print("Speed Cameras:")
        for row in speedCams:
            print(f"  {row[0]} : {row[1]}")
    print()
##################################################################  

#
# percent_Violation
#
# Given a connection to the database and a violation date,
# checks to see if violation date exists in both camera systems and returns the total violations and their percentages in respects of eachother

def percent_Violation(dbConn, search):
    redCamera = check_Exists(dbConn, "RedViolations", "Violation_Date", search)
    speedCamera = check_Exists(dbConn, "SpeedViolations", "Violation_Date", search)


    if not redCamera and not speedCamera:
        print("No violations on record for that date.")
        print()
        return
    else:
        dbCursor = dbConn.cursor()
        dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations WHERE Violation_Date = ?", (search,))
        redViol = dbCursor.fetchone()
            
        dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations WHERE Violation_Date = ?", (search,))
        speedViol = dbCursor.fetchone()

        redNum = redViol[0]
        speedNum = speedViol[0]
        total = redNum + speedNum
        redPercent = (redNum / total) *100
        speedPercent = (speedNum / total) *100
        print("Number of Red Light Violations:", f"{redNum:,}", f"({redPercent:.3f}%)")
        print("Number of Speed Violations:", f"{speedNum:,}", f"({speedPercent:.3f}%)")
        print("Total Number of Violations:", f"{total:,}")
    print()

##################################################################  

#
# cams_At_Intersection
#
# Given a connection to the database, returns the number of cameras at each intersection and their percentages in respect to the total number of cameras


def cams_At_Intersection(dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT i.Intersection, i.Intersection_ID, COUNT(c.Camera_ID) AS Count, SUM(COUNT(c.Camera_ID)) OVER() As Total from Intersections i Join RedCameras c on i.Intersection_ID = c.Intersection_ID Group by i.Intersection Order by Count Desc, i.Intersection_ID Desc")
    redCameras = dbCursor.fetchall()

    totalRed = redCameras[0][3]
    
    print("Number of Red Light Cameras at Each Intersection")
    for row in redCameras:
        camCt = row[2]
        print(f"  {row[0]} ({row[1]}) : {camCt} ({((camCt/totalRed)*100):.3f}%)")
    print()

    dbCursor.execute("SELECT i.Intersection, i.Intersection_ID, COUNT(c.Camera_ID) AS Count, SUM(COUNT(c.Camera_ID)) OVER() As Total from Intersections i Join SpeedCameras c on i.Intersection_ID = c.Intersection_ID Group by i.Intersection Order by Count Desc, i.Intersection_ID Desc")
    speedCameras = dbCursor.fetchall()

    totalSpeed = speedCameras[0][3]

    print("Number of Speed Cameras at Each Intersection")
    for row in speedCameras:
        camCt = row[2]
        print(f"  {row[0]} ({row[1]}) : {camCt} ({((camCt/totalSpeed)*100):.3f}%)")
    print()

##################################################################  

#
# year_Violation
#
# Given a connection to the database and a year, returns total number of violations from each type of camera and their respective percentages
#

def year_Violation(dbConn, search):
    print()
    key = "%" + search + "%"
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT i.Intersection, i.Intersection_ID, SUM(v.Num_Violations) AS Sum, SUM(SUM(v.Num_Violations)) OVER () As Total from Intersections i Join RedCameras c on i.Intersection_ID = c.Intersection_ID Join RedViolations v on v.Camera_ID = c.Camera_ID Where v.Violation_Date like ? Group by i.Intersection Order by Sum Desc, i.Intersection_ID Desc", (key,))
    redCameras = dbCursor.fetchall()


    
    print("Number of Red Light Violations at Each Intersection for", search)
    if len(redCameras) == 0:
        print("No red light violations on record for that year.")
    else:
        totalRed = redCameras[0][3]
        for row in redCameras:
            camCt = row[2]
            print(f"  {row[0]} ({row[1]}) : {camCt:,} ({((camCt/totalRed)*100):.3f}%)")
        print("Total Red Light Violations in ", search," : ", f"{totalRed:,}")
    print()

    dbCursor.execute("SELECT i.Intersection, i.Intersection_ID, SUM(v.Num_Violations) AS Sum, SUM(SUM(v.Num_Violations)) OVER () As Total from Intersections i Join SpeedCameras c on i.Intersection_ID = c.Intersection_ID Join SpeedViolations v on v.Camera_ID = c.Camera_ID Where v.Violation_Date like ? Group by i.Intersection Order by Sum Desc, i.Intersection_ID Desc", (key,))
    speedCameras = dbCursor.fetchall()


    print("Number of Speed Violations at Each Intersection for", search)
    if len(speedCameras) == 0:
        print("No speed violations on record for that year.")
    else:
        totalSpeed = speedCameras[0][3]
        for row in speedCameras:
            camCt = row[2]
            print(f"  {row[0]} ({row[1]}) : {camCt:,} ({((camCt/totalSpeed)*100):.3f}%)")
        print("Total Speed Violations in ", search," : ", f"{totalSpeed:,}")
    print()

##################################################################  

#
# create_Year_Graph

# Creates a plot for yearly violations

def create_Year_Graph(table, number):
    print()
    response = input("Plot? (y/n) ")
    if response == "y":
        years = [row[0] for row in table]
        value = [row[1] for row in table]
        plt.plot(years, value, linestyle='-', color='b', label=f"Yearly Violtations for Camera {number}")
        plt.xlabel("Year")
        plt.ylabel("Number of Violations")
        plt.title(f"Yearly Violtations for Camera {number}")
        plt.show()

##################################################################  

#
# create_Comp_Graph

# Creates comparison graph for each day of the given year

def create_Comp_Graph(speedTable, redTable, number):
    print()
    response = input("Plot? (y/n) ")
    if response == "y":
        date = [row[0] for row in speedTable]
        value = [row[1] for row in speedTable]

        dayCount = [datetime.datetime.strptime(day, '%Y-%m-%d') for day in date]
        offset = [(day - datetime.datetime(day.year, 1, 1)).days for day in dayCount]
        dayAxis = [0]
        violAxis = [0]
        dayAxis.extend(offset)
        violAxis.extend(value)

        plt.plot(dayAxis, violAxis, linestyle='-', label='Speed Violations')

        date = [row[0] for row in redTable]
        value = [row[1] for row in redTable]

        dayCount = [datetime.datetime.strptime(day, '%Y-%m-%d') for day in date]
        offset = [(day - datetime.datetime(day.year, 1, 1)).days for day in dayCount]
        dayAxis = [0]
        violAxis = [0]
        dayAxis.extend(offset)
        violAxis.extend(value)
        plt.plot(dayAxis, violAxis, linestyle='-', label='Red Light Violations')

        plt.xlabel("Day")
        plt.ylabel("Number of Violations")
        plt.title(f"Violations Each Day of {number}")
        plt.xticks(range(0,365,50))


        plt.legend()
        plt.show()

##################################################################  

#
# create_street_Graph

# Creates map plot graph of given street and the red light/speed cameras along that street

def create_street_Graph(redX,redY,redID, speedX,speedY,speedID, search):
    print()
    response = input("Plot? (y/n) ")
    if response == "y":

        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  

        plt.imshow(image, extent=xydims)
        plt.title(f"Cameras on Street: {search}")
        plt.plot(redX, redY,'o-')
        plt.plot(speedX, speedY,'o-')

        for i in range(len(redX)):
            plt.annotate(redID[i], (redX[i], redY[i]))

        
        for i in range(len(speedX)):
            plt.annotate(speedID[i], (speedX[i], speedY[i]))

        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()

##################################################################  

#
# create_Month_Graph

# Creates a graph for all monthly violations within a given year

def create_Month_Graph(table, number, year):
    print()
    response = input("Plot? (y/n) ")
    if response == "y":
        months = [row[1] for row in table]
        value = [row[2] for row in table]
        plt.plot(months, value, linestyle='-', color='b', label=f"Monthly Violtations for Camera {number} ({year})")
        plt.xlabel("Year")
        plt.ylabel("Number of Violations")
        plt.title(f"Monthly Violtations for Camera {number} ({year})")
        plt.show()

##################################################################  

#
# check_Cam_ID
#
# Given a connection to the database and a Camera ID,
# checks if the id exists in either system and returns all yearly violations of a specific camera

def check_Cam_ID(dbConn, search):
    dbCursor = dbConn.cursor()


    dbCursor.execute("Select strftime('%Y', v.Violation_Date),SUM(v.Num_Violations) as TotalViolations From RedViolations v Join RedCameras c on c.Camera_ID = v.Camera_ID Where c.Camera_ID = ? Group by strftime('%Y', v.Violation_Date) Order by strftime('%Y', v.Violation_Date) ASC", (search,))
    redViol = dbCursor.fetchall()

    redCamera = check_Exists(dbConn, "RedCameras", "Camera_ID", search)
    speedCamera = check_Exists(dbConn, "SpeedCameras", "Camera_ID", search)

    if redCamera:
        camTable = "RedCameras"
        violTable = "RedViolations"
    elif speedCamera:
        camTable = "SpeedCameras"
        violTable = "SpeedViolations"
    else:
        print("No cameras matching that ID were found in the database.")
        print()
        return

    dbCursor.execute(f"Select strftime('%Y', v.Violation_Date),SUM(v.Num_Violations) as TotalViolations From {violTable} v Join {camTable} c on c.Camera_ID = v.Camera_ID Where c.Camera_ID = ? Group by strftime('%Y', v.Violation_Date) Order by strftime('%Y', v.Violation_Date) ASC", (search,))
    results = dbCursor.fetchall()
    print("Yearly Violations for Camera",search)
    for row in results:
        print(f"{row[0]} : {row[1]:,}")
    create_Year_Graph(results, search)
    print()


################################################################## 

#
# check_Cam_ID_Month
#
# Given a connection to the database and a Camera ID,
# checks if the id exists in either system and returns all monthly of a specific camera at a given year

def check_Cam_ID_Month(dbConn, search):
    camTable = "null"
    violTable = "null"
    redCamera = check_Exists(dbConn, "RedCameras", "Camera_ID", search)
    speedCamera = check_Exists(dbConn, "SpeedCameras", "Camera_ID", search)


    if redCamera:
        camTable = "RedCameras"
        violTable = "RedViolations"
    elif speedCamera:
        camTable = "SpeedCameras"
        violTable = "SpeedViolations"
    else:
        print("No cameras matching that ID were found in the database.")
        print()
        return
    
    year = input("Enter a year: ")

    dbCursor = dbConn.cursor()
    dbCursor.execute(f"Select strftime('%m/%Y', v.Violation_Date),strftime('%m', v.Violation_Date),SUM(v.Num_Violations) as TotalViolations From {violTable} v Join {camTable} c on c.Camera_ID = v.Camera_ID Where c.Camera_ID = ? and strftime('%Y', v.Violation_Date) = ? Group by strftime('%m/%Y', v.Violation_Date) Order by strftime('%m/%Y', v.Violation_Date) ASC", (search, year))
    results = dbCursor.fetchall()
    print(f"Monthly Violations for Camera {search} in {year}")
    for row in results:
        print(f"{row[0]} : {row[2]:,}")
    create_Month_Graph(results,search,year)
    print()

################################################################## 

#
# violation_By_Day
#
# Given a connection to the database and a Year,
# returns list of first and last 5 total violations of a given Year and prompts user to create a graph based on data

def violation_By_Day(dbConn, search):
    key = f"%{search}%"
    dbCursor = dbConn.cursor()
    dbCursor.execute(f"SELECT Violation_Date, SUM(Num_Violations) AS TotalViolations FROM RedViolations WHERE Violation_Date LIKE ? GROUP BY Violation_Date ORDER BY Violation_Date ASC", (key,))
    results = dbCursor.fetchall()

    firstFive = results[:5]
    lastFive = results[-5:]

    print("Red Light Violations:")
    for row in firstFive:
        print(f"{row[0]} {row[1]}")
    for row in lastFive:
        print(f"{row[0]} {row[1]}")

    dbCursor.execute(f"SELECT Violation_Date, SUM(Num_Violations) AS TotalViolations FROM SpeedViolations WHERE Violation_Date LIKE ? GROUP BY Violation_Date ORDER BY Violation_Date ASC", (key,))
    speedResults = dbCursor.fetchall()

    firstFive =  speedResults[:5]
    lastFive =  speedResults[-5:]

    print("Speed Violations:")
    for row in firstFive:
        print(f"{row[0]} {row[1]}")
    for row in lastFive:
        print(f"{row[0]} {row[1]}")
    create_Comp_Graph(speedResults, results, search)
    print()

################################################################## 

#
# camera_By_Street
#
# Given a connection to the database and Street name, returns all cameras from that street, both red light and speed, and then prompts the user to create a graph

def camera_By_Street(dbConn, search):
    key = f"%{search}%"
    dbCursor = dbConn.cursor()
    dbCursor.execute(f"Select Camera_ID, Address, Latitude, Longitude From RedCameras Where Address like ? Order by Camera_ID ASC", (key,))
    redCameras = dbCursor.fetchall()
    dbCursor.execute(f"Select Camera_ID, Address, Latitude, Longitude From SpeedCameras Where Address like ? Order by Camera_ID ASC", (key,))
    speedCameras = dbCursor.fetchall()

    if not redCameras and not speedCameras:
        print("There are no cameras located on that street.")
        print()
        return


    redX = []
    redY = []
    redID = []

    speedX = []
    speedY = []
    speedID = []

    print() 
    print(f"List of Cameras Located on Street: {search}")
    print("  Red Light Cameras:")
    for row in redCameras:
        redID.append(row[0])
        redX.append(row[3])
        redY.append(row[2])
        print(f"    {row[0]} : {row[1]} ({row[2]}, {row[3]})")
    print("  Speed Cameras:")
    for row in speedCameras:
        speedID.append(row[0])
        speedX.append(row[3])
        speedY.append(row[2])
        print(f"    {row[0]} : {row[1]} ({row[2]}, {row[3]})")
    create_street_Graph(redX,redY,redID, speedX,speedY,speedID, search)
    print()

################################################################## 
# MAIN MENU
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

user_input = "null"

while user_input != "x":
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")
    user_input = input("Your choice --> ")

    if user_input ==  "1":
        print()
        intersection = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")
        print_intersections(dbConn, intersection)
    elif user_input == "2":
        print()
        intersection = input("Enter the name of the intersection (no wildcards allowed): ")
        find_Cameras(dbConn, intersection)
    elif user_input == "3":
        print()
        date = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ")
        percent_Violation(dbConn, date)
    elif user_input == "4":
        print()
        cams_At_Intersection(dbConn)
        print()
    elif user_input == "5":
        print()
        year = input("Enter the year that you would like to analyze: ")
        year_Violation(dbConn, year)
    elif user_input == "6":
        print()
        camera = input("Enter a camera ID: ")
        check_Cam_ID(dbConn, camera)
    elif user_input == "7":
        print()
        camera = input("Enter a camera ID: ")
        check_Cam_ID_Month(dbConn, camera)
    elif user_input == "8":
        print()
        year = input("Enter a year: ")
        violation_By_Day(dbConn,year)
    elif user_input == "9":
        print()
        street = input("Enter a street name: ")
        camera_By_Street(dbConn, street)
    elif user_input != "x":
        print("Error, unknown command, try again...")
        print()

    





print("Exiting program.")
#
# done
#
