# Transportation-Scheduller

This is a program which uses the PuLP library to optimally allocates drivers to routes, minimizing the difference in start times and taking into account the licence requirements of the route.

The program will read an excel file containing the infomation for the drivers and routes, and will append the allocated driver to the route. Any drivers that have not been allocated because there is no available route within +/- 90 minutes of their start time, will be highlighted red on the worksheet.

# Libraries

To be able to run this program you will need to install the following libraries:

- [Pandas](https://pandas.pydata.org/)
- [Numpy](https://numpy.org/)
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
- [PuLP](https://pypi.org/project/PuLP/)
- [itertools](https://docs.python.org/3.4/library/itertools.html)


# Introduction

I created this program because i noticed that typically the allocation of drivers to routes was a manual process, which could be automated. The model set up using the PuLP library only optimizes the difference in start time, however, you could tailor the model to make the model take into account overtime or any other factor. 

I have set up the following constaints:

- A driver can not be planned more than once.
- A route can not appear in the solution more than once.
- A driver with class 2 HGV licence can only be allocated to a route with a class 2 HGV licence requirement.

# Installation

You will need to install Python onto your local computer and install the packages in ```Libraries```.

You will need to ammend the variable i have assigned to the name of the Excel file to match your Excel file. This file will need the columns described below with the same names.

```name = "test.xlsx"```

## Excel File

As i mentioned previously the program reads an excel file for the information.

The file should include the following columns:

- ```Driver``` : Column containing driver name
- ```Driver Start Time``` : Column containing driver start time
- ```Driver Class``` : Class of driver's HGV licence

- ```Route``` : Route identifier
- ```Route Start Time``` : Start time of route
- ```Route Class``` : HGV licence requirement.

- The program will append the solution into column G.


# License

Distributed under the MIT Licence. See ```LICENSE``` for more information.

# Contact

John Abel - [johnabel1997@gmail.com](johnabel1997@gmail.com)


# Acknowledgements

- [https://benalexkeen.com/linear-programming-with-python-and-pulp-part-5/](https://benalexkeen.com/linear-programming-with-python-and-pulp-part-5/)


