#import libraries
from pulp import *

import pandas as pd
import numpy as np
import openpyxl
import itertools
import datetime

import tkinter as tk
from tkinter import filedialog as fd


import warnings
warnings.simplefilter(action='ignore')



def read_excel(name):
    """
    Function to read excel file using pandas .read_excel()

    ARGS: Excel file that contains routes and drivers.
          Expected to be 6 columns:
              - Driver Start in HH:MM format
              - Driver Name
              - Driver license
              - Route Start in HH:MM format
              - Route
              - route license


    OUTPUT: Output will return itertools product object with combinations of routes and drivers with their respective start
            times.

    """

    data = pd.read_excel(name)

    data['Driver Start Time']= pd.to_datetime(data['Driver Start Time'])
    data['Route Start Time']= pd.to_datetime(data['Route Start Time'])

    drivers = data[['Driver','Driver Start Time','Driver Class']]

    routes = data[['Route','Route Start Time','Route Class']]
    #Remove NaN values

    drivers.dropna(inplace=True)
    routes.dropna(inplace=True)

    #Combine drivers and route together to create every possible combination

    combination_names = itertools.product(drivers['Driver'],routes['Route'])

    combination_times = itertools.product(drivers['Driver Start Time'], routes['Route Start Time'])

    class_combination = itertools.product(drivers['Driver Class'],routes['Route Class'])

    #Join combinations together

    combinations = list(zip(combination_names,combination_times,class_combination))

    #Filter out combinations with driver class 2 license and route class 1 license.

    for item in combinations:
        if item[2] == ('class 2','class 1'):
            combinations.remove(item)

    return combinations


def calculate_difference(time1,time2):

    """
    Function to calculate difference in times.

    ARGS: two times in datetime format

    OUTPUT: Returns a value based on the difference in minutes. As the problem is trying to maximize -
            i have given differences that are small large values, and differences that are larger than 90 minutes
            negative values. This means that the model will not plan undesirable routes.

    """

    difference = abs(time1 - time2)

    difference = difference.total_seconds()/60

    if difference < 15:
        diff = 500
    elif difference < 30:
        diff = 250
    elif difference < 60:
        diff = 75
    elif difference < 90:
        diff = 10
    else:
        diff = -100


    return diff

def createCombinationDict(combinations):

    """
    Function to create a dictionary for driver,route combination and the difference in start times.

    ARGS: Input an iteratable - list or in this instance an intertool product object.

    OUTPUT: Returns a dictionary. Route, driver combination as key and a a tuple as the value containing
            difference in start time and the respective license of the driver and route.

    """
    combination_dict = {}

    for item in combinations:

        combination_dict[item[0]] = (calculate_difference(item[1][0],item[1][1]), item[2])
    return combination_dict

def setUpModel(dictionary,LpType=LpMaximize):

    """
    Function to set up PuLp model.

    ARGS: The dictionary with combinations and values.

    Optional Args: LpType - set to LpMinimize so that the model minimizes a function but can be set to LpMaximize

    returns model set up with variables and function.

    This sets the model to minimize the difference in start time.
    """

    combinations = []

    for item in dictionary.keys():
        combinations.append(item)

    allocation_model = pulp.LpProblem('Allocate Drivers',LpType)

    return allocation_model

def setUpConstraints(allocation_model,dictionary, combinations,x):

    """
    Function to set up contraints.

    args: allocation model, which has been set up, and a list of combinations.
    Dictionary containing combinations and values, x as an LpVariable object.

    returns: model set up with constraints

    """
    #Creating sets for unique routes and drivers.

    #Disallowed list: List of driver combinations which are not allowed - Class 2 driver Class 1 route.

    routes = set()
    driver = set()

    disallowed = []


    for item in dictionary.keys():
        routes.add(item[1])
        driver.add(item[0])

        if dictionary[item][1] == ('class 2','class 1'):
            disallowed.append(item)


    #Contraint 1: Routes con only appear in solution once, however as we will most likely have more routes than drivers
    # its less than or equal to 1.

    for route in routes:

        allocation_model += pulp.lpSum([x[combination] for combination in combinations if route in combination]) <= 1

    """
    Constaint 2: Making sure drivers are not planned more than once. As i have set the problem to LpMaximize -
    it will favour planning a driver to a route. As i have given arbituary values to optimize, with negative values for
    undesirable drivers, it means the model would rather leave a route unassigned than assign an undesirable driver.
    """

    for driver in driver:
        allocation_model += pulp.lpSum([x[combination] for combination in combinations if driver in combination]) <= 1


    #Constraint 3: Ensuring the driver has the correct license for the route.

   # allocation_model += sum([x[combination] for combination in combinations if combination in disallowed]) == 0

    return allocation_model


def findSolution(solved_model,dictionary,x):
    combinations = []
    for item in dictionary.keys():
        combinations.append(item)
    solution = {}
    for combination in combinations:
        if x[combination].value() == 1.0:
            solution[combination[1]] = combination[0]

    return solution

def addSolution(solution,name):

    """
    Function to append solved solution to excel file.

    args: Dictionary containing routes as keys and planend drivers as values. The location of filename and path as name.

    Output: Function returns sheet object.

    """


    #Open excel file

    wb = openpyxl.load_workbook(name)

    sheet = wb.get_sheet_by_name('Plan')

    routes = []
    for i in range(2,len(sheet['A'])):
        routes.append(sheet['A' + str(i)].value)
        try:
            sheet['F' + str(i)].value = solution[sheet['A' + str(i)].value]
        except:
            continue

    return wb


def checkSolution(solution,wb,dictionary,name):

    """
    Function to check solution to highlight drivers which have not been planned and to highlight drivers who have been
    planned > 60 minutes from their start time.

    args: sheet object, solution dictinary and dictionary containing combinations and differences in start time. Name expected filename string

    output: The function does not return anything - it will complete checks and save the workbook.

    """
    from openpyxl.styles import Font
    from openpyxl.styles.colors import RED,BLACK

    sheet = wb.get_sheet_by_name('Plan')

    for i in range(2,len(sheet['I'])):

        if sheet['I' + str(i)].value not in solution.values():
            sheet['I' + str(i)].font = Font(color = RED)

        else:
            sheet['I' + str(i)].font = Font(color=BLACK)


    wb.save(name)


def main(Name):


    combinations = list(read_excel(name))

    dictionary = createCombinationDict(combinations)

    allocation_model = setUpModel(dictionary)

    combinations = []

    for item in dictionary.keys():
        combinations.append(item)

    x = pulp.LpVariable.dicts('combination', combinations, lowBound=0, upBound = 1, cat = LpInteger)

    allocation_model += pulp.lpSum([dictionary[route][0] * x[route] for route in combinations])

    allocation_model = setUpConstraints(allocation_model,dictionary,combinations,x)

    solved_model = allocation_model.solve()

    solution = findSolution(solved_model,dictionary,x)

    wb = addSolution(solution,name)

    checkSolution(solution,wb,dictionary,name)

    print("Allocation complete: \n")

    for route in solution:
        print(route + ":"+  solution[route])


if __name__ == '__main__':

    name = "test.xlsx"



    main(name)
