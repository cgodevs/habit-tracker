from frames import *
from random import choices
from pixela import *
from time import sleep
from functools import partial
from sys import exit

graph_requirements = "id  is an ID for identifying the pixelation graph.\n " \
                     "Validation rule: ^[a-z][a-z0-9-]{1,16}\n\n"\
                     "Name is the name of pixelation graph\n\n"\
                     "Unit is a unit of the quantity recorded in the pixelation graph." \
                     "\nEx. commit, kilogram, calory.\n\n"\
                     "Color Defines the display color of the pixel in the pixelation graph.\n"\
                     "Options: shibafu (green), momiji (red), sora (blue),ichou (yellow),\n" \
                     "ajisai (purple) and kuro (black) are supported as color kind.\n\n" \
                     "(Unit TYPE is a float by default)"


class MainProgram:
    def __init__(self, root: Tk, canvas: Canvas):
        self.root = root
        self.canvas = canvas

        self.dateframe = DateFrame(self.root)  # a DateFrame will always exist, given a date must always be present
        self.timeframe = TimeFrame(self.root)  # TimeFrame will depend on the unit of a graph to be gridded in window
        self.inputframe = InputFrame(self.root, unit='None')  # And so will InputQuantity

        self.menu = MainMenu(self)
        self.root.config(menu=self.menu)
        self.buttons: PixelaActions

        try:
            with shelve.open(filename='user_options') as sf:
                self.pixela = PixelaManager(username=sf["username"], token=sf["token"])
                self.pixela.get_graph_details()
        except (KeyError, FileNotFoundError):
            self.pixela = PixelaManager(username=None, token=None)

        try:
            with shelve.open(filename='user_options') as sf:
                self.menu.login_from_graph_name_option(sf['graph_name'])
                self.menu.display_all_graphs_to_access()
        except (KeyError, FileNotFoundError):
            LoginWindow(self)


class MainMenu(Menu):
    def __init__(self, program: MainProgram):
        super().__init__(program.root)
        self.program = program
        self.new_user_window: NewUserWindow
        self.new_graph: CreateGraphWindow

    # |File      _ □ x|
        self.file_menu = Menu(self, tearoff=False)
        self.add_cascade(label="File", menu=self.file_menu)

        self.choose_habit = Menu(self.file_menu, tearoff=False)
        self.file_menu.add_cascade(label="Habits", menu=self.choose_habit)
        self.choose_habit.add_command(label="New Habit", command=self.create_new_graph)

        self.delete_menu = Menu(self.file_menu, tearoff=False)
        self.choose_habit.add_cascade(label="Delete Habit", menu=self.delete_menu)
        self.choose_habit.add_separator()
        self.entryconfig("File", state="disabled")  # File menu is disabled at start

    # |File Option    _ □ x|
        self.option_menu = Menu(self, tearoff=False)
        self.add_cascade(label="Option", menu=self.option_menu)
        self.date_format = Menu(self.option_menu, tearoff=False)
        self.option_menu.add_cascade(label="Date Format", menu=self.date_format)

        self.date_format.add_command(label="American Format",
                                     command=partial(self.change_date_format, 'mm/dd/yyyy'))
        self.date_format.add_command(label="European Format",
                                     command=partial(self.change_date_format, 'dd/mm/yyyy'))
        self.date_format.add_command(label="Asian Format",
                                     command=partial(self.change_date_format, 'yyyy/mm/dd'))
        self.entryconfig("Option", state="disabled")  # Option menu is disabled at start

    # |File Option Login     _ □ x|
        self.login_menu = Menu(self, tearoff=False)
        self.add_cascade(label="Login", menu=self.login_menu)

        self.login_menu.add_command(label="Enter", command=self.initial_login)
        self.login_menu.add_separator()
        self.login_menu.add_command(label="New User", command=self.new_user_screen)
       
    def destroy_canvas(self):
        try:
            self.program.canvas.grid_forget()
            self.program.root.config(padx=25, pady=30, bg=BACKGROUND_COLOR)
        except:
            pass

    def initial_login(self):
        LoginWindow(self.program)

    def change_date_format(self, what_format):  # 'mm/dd/yyyy', 'dd/mm/yyyy' or 'yyyy/mm/dd'
        self.program.dateframe.change_date_pattern(what_format)

    def new_user_screen(self):
        self.new_user_window = NewUserWindow(self.program)

        if self.new_user_window.successfully_created:  # then there already are username and token in program.pixela
            self.new_user_window.destroy()   # menu will no longer acknowledge its new_user attribute
            self.new_graph = CreateGraphWindow(self.program)

            if self.new_graph.successfully_created:
                self.new_graph.destroy()

                # Log in again to reset the screen with the new graph info
                LoginWindow(program=self.program, user_just_created=True)
                self.file_menu.entryconfig("Habits", state="disabled")

    def create_new_graph(self):
        self.new_graph = CreateGraphWindow(self.program)

        if self.new_graph.successfully_created:
            self.new_graph.destroy()

            # Log in again to reset the screen with the new graph info
            LoginWindow(program=self.program)
            self.file_menu.entryconfig("Habits", state="disabled")  # weird bug will cause menu graphs concatenation

    def display_all_graphs_to_access(self):
        for graph in self.program.pixela.all_graphs_info:
            self.choose_habit.add_command(
                label=f"{graph['name']}",
                command=partial(self.login_from_graph_name_option, graph['name']))
            self.delete_menu.add_command(
                label=f"{graph['name']}",
                command=partial(self.delete_graph_from_menu, graph['graphID'])
            )

    def login_from_graph_name_option(self, name):
        self.program.pixela.set_graph_choice(name)
        LoginWindow(program=self.program, name=name)
        with shelve.open(filename='user_options') as sf:
            sf['graph_name'] = name

    def delete_graph_from_menu(self, graph_id):
        self.program.pixela.delete_graph(graph_id)


class LoginWindow(Toplevel):
    """
    In case of: Enter > Login
    In case of: New User > New Graph > Login (with delay) or
    In case of: Login > New Graph > Login (again to display new graph)
    This class feeds the main program with a pixela for username and token
    """

    def __init__(self, program: MainProgram, user_just_created=False, name=None):
        self.root = program.root
        self.program = program
        self.user_just_created = user_just_created
        self.name = name  # to be used by function "login_from_graph_name_option"
        super().__init__(program.root)

        if self.program.pixela.username is not None and self.program.pixela.token is not None:
            self.login(self.program.pixela.username, self.program.pixela.token)
            return

        # ------------------------- Griding Login Window ------------------------------- #
        self.title("Login")
        self.geometry("200x120")
        self.iconbitmap("img\\anvil.ico")
        Label(self, text="Username: ").grid(row=0, column=0, pady=(5, 0), padx=5, sticky='e')
        self.username_entry = Entry(self, width=16)
        self.username_entry.grid(row=0, column=1, pady=(5, 0), padx=5)
        self.username_entry.focus()

        Label(self, text="Token: ", pady=5).grid(row=1, column=0, padx=5, sticky='e')
        self.token_entry = Entry(self, width=16)
        self.token_entry.grid(row=1, column=1, pady=5)

        # variable to hold on to checked state, 0 is off, 1 is on.
        self.checked_state = IntVar()
        self.checkbutton = Checkbutton(self, text="Remember Me",
                                       variable=self.checked_state,
                                       onvalue=1, offvalue=0)
        self.checkbutton.grid(row=2, column=0, columnspan=2)

        self.enter = Button(self, text="Log in", command=self.login, width=10)
        self.enter.grid(row=3, column=0, columnspan=2, pady=10, padx=(10, 0))

        self.mainloop()
        # ------------------------------------------------------------------------------- #

    def login(self, u=None, t=None):
        if u is None and t is None:
            username = self.username_entry.get()
            token = self.token_entry.get()
            if username == '' or token == '':
                messagebox.showwarning(title="Fields Required", message="Please input both Username and Token")
                self.focus()
                self.username_entry.focus()
                return
            else:
                if self.checked_state.get() == 1:
                    self.remember_user(username, token)
        else:
            username = u
            token = t

        # redundant if user was already logged, relevant for new login or new user:
        if self.name is None:
            self.program.pixela = PixelaManager(username, token)

        if self.user_just_created:
            # if an user has just been created, immediate request
            # to check if user exists may bring back wrong results
            sleep(2)

        if self.program.pixela.is_validated_user(username):
            if self.name is None:
                self.program.pixela.get_graph_details()  # populates {graphID}, {graph name}, {unit}, {is_time_unit}
            self.program.root.title(f"({username}) {self.program.pixela.graph_name}")
            self.program.menu.destroy_canvas()
            self.set_user_screen()
            self.destroy()
            return True
        else:
            messagebox.showerror(title="User Not Found", message="Not possible to log in")
            self.focus()
            self.username_entry.focus()

    def set_user_screen(self):

        # to avoid cases where user changes between graphs, widgets are destroyed, but not the frames,
        # so they can be gridded over and over again and NOT overlap with the previous one
        self.destroy_every_widget()
        self.program.dateframe = DateFrame(self.root)  # DateFrame and Buttons will always be gridded
        self.program.dateframe.grid(row=0, column=0, columnspan=4)

        if self.program.pixela.is_time_unit:
            self.program.timeframe = TimeFrame(self.root)
            self.program.timeframe.grid(row=2, column=0, columnspan=4)
        else:
            self.program.inputframe = InputFrame(self.root, self.program.pixela.graph_unit)
            self.program.inputframe.grid(row=2, column=0, columnspan=4)

        self.program.buttons = PixelaActions(self.program)

        self.program.menu.entryconfig("File", state="normal")
        self.program.menu.entryconfig("Option", state="normal")
        self.program.menu.login_menu.entryconfig("Enter", state="disabled")
        self.program.menu.login_menu.add_separator()
        self.program.menu.login_menu.add_command(label="Log Out", command=self.logout)
        if self.name is None:
            self.program.menu.display_all_graphs_to_access()

    def remember_user(self, username, token):
        with shelve.open(filename='user_options') as sf:
            sf['username'] = username
            sf['token'] = token

    def destroy_every_widget(self):
        # destroy all widgets from frame
        for widget in self.program.timeframe.winfo_children():
            widget.destroy()
        self.program.timeframe.grid_forget()

        for widget in self.program.dateframe.winfo_children():
            widget.destroy()
        self.program.dateframe.grid_forget()

        for widget in self.program.inputframe.winfo_children():
            widget.destroy()
        self.program.inputframe.grid_forget()

    def logout(self):
        try:
            with shelve.open('user_options') as sf:
                del sf['username']
                del sf['token']
        except (FileNotFoundError, KeyError):
            pass
        exit()

class NewUserWindow(Toplevel):
    def __init__(self, program: MainProgram):
        self.program = program
        self.root = program.root
        self.successfully_created = False
        super().__init__(self.root)

        self.title("New User")
        self.geometry("200x160")
        self.iconbitmap("img\\anvil.ico")

        Label(self, text="Username: ").grid(row=0, column=0, pady=(5, 0), padx=5, sticky='e')
        self.username_entry = Entry(self, width=16)
        self.username_entry.grid(row=0, column=1, pady=(5, 0), padx=5)
        self.username_entry.focus()

        Label(self, text="Token: ").grid(row=1, column=0, padx=5, sticky='e')
        self.token_entry = Entry(self, width=16)
        self.token_entry.grid(row=1, column=1, pady=5)
        Label(self, text="Remember to keep your token",
              font=("calibri", 8, "normal")).grid(row=2, padx=5, columnspan=2)
        self.generate_button = Button(self,
                                      text="Generate Token For Me",
                                      width=20,
                                      command=self.generate_token)
        self.create_user_button = Button(self,
                                         text="Create New User",
                                         width=15,
                                         command=self.create_user)

        self.generate_button.grid(row=3, column=0, columnspan=2, pady=(0, 5), padx=(10, 0))
        self.create_user_button.grid(row=4, column=0, columnspan=2, pady=(10, 0), padx=(10, 0))
        self.mainloop()

    def generate_token(self):
        chars = '.!?0123456789abcdefghijklmnopqrstuvxywzABCDEFGHIJKLMNOPQRSTUVXYWZ'
        strong_password = ''.join(choices(chars, k=8))
        self.token_entry.delete(0, END)  # to avoid concatenation when user clicks the button multiple times
        self.token_entry.insert(0, strong_password)

    def create_user(self):
        username = self.username_entry.get()
        token = self.token_entry.get()
        if username == '' or token == '':
            return
        if self.program.pixela.create_user(username, token):
            self.program.pixela = PixelaManager(username, token)
            self.successfully_created = True
            self.quit()
        else:
            self.focus()


class CreateGraphWindow(Toplevel):
    def __init__(self, program: MainProgram):
        # required: username, token, graphID, name, unit, color  # all strings
        self.root = program.root
        self.program = program
        self.successfully_created = False
        super().__init__(self.root)

        self.title("New Graph")
        self.geometry("375x400")
        self.iconbitmap("img\\anvil.ico")

        Label(self, text="Graph ID: ").grid(row=0, column=0, pady=(5, 0), sticky='e')
        self.graphID_entry = Entry(self, width=16)
        self.graphID_entry.grid(row=0, column=1, pady=(5, 0))
        self.graphID_entry.focus()

        Label(self, text="Name: ", pady=5).grid(row=1, column=0, sticky='e')
        self.graph_name_entry = Entry(self, width=16)
        self.graph_name_entry.grid(row=1, column=1, pady=5)

        Label(self, text="Color: ").grid(row=2, column=0, sticky='e')
        self.graph_color_entry = Entry(self, width=16)
        self.graph_color_entry.grid(row=2, column=1)

        Label(self, text="Unit: ").grid(row=3, column=0, pady=(5, 0), sticky='e')
        self.graph_unit_entry = Entry(self, width=16)
        self.graph_unit_entry.grid(row=3, column=1, pady=(5, 0))

        self.enter = Button(self, text="Create Graph", command=self.create_graph, width=15)
        self.enter.grid(row=4, column=0, columnspan=2, pady=10, padx=(10, 0))
        Label(self, text=graph_requirements).grid(row=5, column=0, columnspan=2, pady=(5, 0), padx=5, sticky='w')

        self.mainloop()

    def create_graph(self):
        if self.program.pixela.create_graph(self.graphID_entry.get(), self.graph_name_entry.get(),
                                            self.graph_unit_entry.get(), self.graph_color_entry.get()):
            self.destroy()
            self.successfully_created = True
            self.quit()
        else:
            self.focus()


class PixelaActions:
    def __init__(self, program: MainProgram):
        self.program = program
        self.manager = program.pixela  # a PixelaManager object contains every needed info

        self.create_button = Button(text="Create", command=self.post_data)
        self.create_button.grid(row=4, column=0, padx=5, pady=(20, 0))
        # Change
        self.change_button = Button(text="Change", command=self.update_data)
        self.change_button.grid(row=4, column=1, padx=5, pady=(20, 0))
        # Delete
        self.delete_button = Button(text="Delete", command=self.delete_data)
        self.delete_button.grid(row=4, column=2, padx=5, pady=(20, 0))
        # See All
        self.see_progress = Button(text="See Progress", command=self.manager.open_progress_page)
        self.see_progress.grid(row=4, column=3, padx=5, pady=(20, 0))

    def collect_data(self):
        unit = self.manager.graph_unit
        quantity = None
        if self.program.timeframe is not None:
            quantity = self.program.timeframe.get_pixela_time()  # retrieved in seconds from TimeRecorder
            if unit.lower() in ['hour', 'hours', 'h']:
                quantity = round(quantity / 3600, 2)
            elif unit.lower() in ['minute', 'minutes', 'mins']:
                quantity = round(quantity / 60, 2)
        elif self.program.inputframe is not None:
            quantity = self.program.inputframe.get_quantity()
        date = self.program.dateframe.date_to_pixela
        return quantity, date, unit

    def post_data(self):
        quantity, date, unit = self.collect_data()
        if quantity is not None:
            msg = f"Data to be sent to Pixe.la: \n" \
                  f"Quantity: {quantity} {unit}\n" \
                  f"Date: {date}\n\n" \
                  f"Do you agree?"
            if messagebox.askokcancel(title="Send Data to Pixe.la?", message=msg):
                self.manager.get_graph_details()
                self.manager.send_pixel(date=date, quantity=quantity)
        else:
            messagebox.showerror(
                title="Error",
                message="Please watch out for the hour and minute entries\n"
                        "These fields must be filled with non-negative integers only.")

    def update_data(self):
        quantity, date, unit = self.collect_data()
        if quantity is not None:
            msg = f"Data to be sent to Pixe.la: \n" \
                  f"Quantity: {quantity} {unit}\n" \
                  f"Date: {date}\n\n" \
                  f"Do you agree?"
            if messagebox.askokcancel(title="Update Data in Pixe.la?", message=msg):
                self.manager.get_graph_details()
                self.manager.update_pixel(date=date, quantity=quantity)
        else:
            messagebox.showerror(
                title="Error",
                message="Please watch out for the hour and minute entries\n"
                        "These fields must be filled with non-negative integers only.")

    def delete_data(self):
        date = self.collect_data()[1]
        self.manager.delete_pixel(date)
