# What it is

A GUI made with tkinter and pixe.la's API to keep track of one's habits

## Use

To keep track of any habit's progress of one's choice, [pixe.la](pixe.la) API can collect user's input data and build them a pixel graph similar to Github's.

![Login Screen](https://github.com/cgodevs/habit-tracker/blob/master/img/screenshots/login_screen.PNG)

One pixel in the graph is data input via this app. The amount is always a float, so user can input values in decimals.

This GUI allows an user to access many resources available by pixe.la. It can:

- Create a new user (choose user's: *username, token*)
- Create a new graph (choose graph's: *id, name, color, unit*)
- Delete a graph
- Post pixel (or Increase the day's existing pixel, if any)
- Put pixel (changes the day's pixel, if any, or inputs)
- Delete pixel
- Open user's graph page in browser

## Screenshots and Features

Artwork theme chosen for illustration is Blacksmiths'

User may create a new user or login for the first time at start.

![](C:\Users\cgodevs\PycharmProjects\Habit Tracker\img\screenshots\login_screen.PNG)

It will recognize the user's graph unit and display a different frame based on it.

![](C:\Users\cgodevs\PycharmProjects\Habit Tracker\img\screenshots\user_logged_any_unit.PNG)

In case the unit chosen was time (in hours or minutes), pixel data may be recorded in real time (option: "Record"), or directly input (option: "Input Time")

![](C:\Users\cgodevs\PycharmProjects\Habit Tracker\img\screenshots\record_frame.PNG)

All found user's graphs are displayed in menu and may be accessed by clicking

![](C:\Users\cgodevs\PycharmProjects\Habit Tracker\img\screenshots\features.png)

The standard initial date format is american (mm/dd/yyyy). The menu's "Option" can be used to change this format.

#### Saved Data

- User's login data (username and token)
- Last graph accessed
- Date format

Data will be saved to .bak, .dir, .dat files. Those must be erased in order to erase all of one's saved data.

## Modules Required

- shelve
- tkcalendar

## *Project Status*

Functional. Not fully developed.

May include more features next. May include bugs I'm not aware of. 

This is my first project as a beginner. So this far I have not been able to formally test it.

## *Acknowledgement*

Thanks a lot to [Angela Yu's Udemy Course](https://www.udemy.com/course/100-days-of-code/) for introducing this very nice API and motivating me to start walking my own steps in python (@angelayu)

Thanks to Al Sweigart for introducing the shelve module in his course [Automate the Boring Stuff with Python](https://www.udemy.com/course/automate/) (@alsweigart), and others
