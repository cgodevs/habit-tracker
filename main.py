from tkinter import *
from random import choice

window = Tk()
window.title("Habits Tracker")
window.iconbitmap("img\\anvil.ico")

intro_screens = [PhotoImage(file='img\\intro00.png'),
                 PhotoImage(file='img\\intro01.png'),
                 PhotoImage(file='img\\intro02.png'),
                 PhotoImage(file='img\\intro03.png'),
                 PhotoImage(file='img\\intro04.png'),
                 PhotoImage(file='img\\intro05.png')]

canvas = Canvas(width=399, height=300, highlightthickness=0)
canvas.create_image(200, 150, image=choice(intro_screens))
canvas.grid(row=0, column=0)

from ui import *

program = MainProgram(window, canvas)

window.mainloop()

# experiment with username: "user0003"
# and token: "67!SHfxu%$U5FB"





























