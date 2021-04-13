import requests
from tkinter import messagebox
import webbrowser

PIXELA_ENDPOINT = "https://pixe.la/v1/users"
time_units = ['hour', 'hours', 'minute', 'minutes', 'mins', 'min', 'h']

# graphID  is an ID for identifying the pixelation graph. Validation rule: ^[a-z][a-z0-9-]{1,16}
# name is name of pixelation graph
# unit is a unit of the quantity recorded in the pixelation graph. Ex. commit, kilogram, calory.
# unit_type is the unit_type of quantity to be handled in the graph. Only int or float are supported.
# color Defines the display color of the pixel in the pixelation graph.
# shibafu (green), momiji (red), sora (blue), ichou (yellow), ajisai (purple) and
# kuro (black) are supported as color kind.


class PixelaManager:
    def __init__(self, username, token):
        self.username = username
        self.token = token
        self.graphID = ''
        self.graph_name = ''
        self.graph_unit = ''
        self.is_time_unit = False   # tells to display the Time Recording Section on the window
        self.all_graphs_info = []

    def create_user(self, user, pw):
        user_params = {
            "token": pw,
            "username": user,
            "agreeTermsofService": "yes",
            "notMinor": "yes"
        }
        response = requests.post(url=PIXELA_ENDPOINT, json=user_params)
        if response.json()["isSuccess"]:
            messagebox.showinfo(
                title="Success!",
                message=f"User '{user}' successfully created.\n"
                        f"Token: {pw}\n"
                        f"Please keep your username and token safe.\n"
                        f"You may create your first graph next.")
            return True
        else:
            pixela_msg = response.json()["message"]
            messagebox.showwarning(
                title="User Not Created",
                message=f'Not Possible to Create user "{user}"\n'
                        f'Message from pixe.la: {pixela_msg}"')
            return False

    def is_validated_user(self, username):
        response = requests.get(url=f"https://pixe.la/@{username}")
        if response.status_code == 404 or '404 page not found' in response.text:
            return False
        else:
            return True

    def get_graph_details(self):
        """
        graph_name won't be empty when this function's called from menu's functions:
        'login_from_graph_name_option' > set_graph_choice(name) > LoginWindow > 'login'
        """
        if self.graph_name == '':
            details_endpoint = f"{PIXELA_ENDPOINT}/{self.username}/graphs"
            headers = {"X-USER-TOKEN": self.token}
            response = requests.get(url=details_endpoint, headers=headers)
            response.raise_for_status()

            graph_details = response.json()['graphs']

            self.all_graphs_info = [  # items are stored by graphId alphabetical order
                {
                    'graphID': item['id'],
                    'name': item['name'],
                    'unit': item['unit'],
                    'is_time_unit': True if item['unit'].lower() in time_units else False
                }
                for item in graph_details]

            self.graphID = self.all_graphs_info[0]['graphID']  # this may be not the last graph created by the user
            self.graph_name = self.all_graphs_info[0]['name']
            self.graph_unit = self.all_graphs_info[0]['unit']
            self.is_time_unit = self.all_graphs_info[0]['is_time_unit']

    def set_graph_choice(self, graph_name):
        for graph in self.all_graphs_info:
            if graph['name'] == graph_name:
                self.graph_name = graph_name
                self.graphID = graph['graphID']
                self.graph_unit = graph['unit']
                self.is_time_unit = graph['is_time_unit']
                break

    def get_pixel(self, date):
        get_pixel_endpoint = f'{PIXELA_ENDPOINT}/{self.username}/graphs/{self.graphID}/{date}'
        headers = {"X-USER-TOKEN": self.token}

        response = requests.get(url=get_pixel_endpoint, headers=headers)
        if 'quantity' in response.json():
            return response.json()['quantity']
        else:
            return 0

    def send_pixel(self, date, quantity):
        found_value = self.get_pixel(date)
        formatted_date = '/'.join([date[4:6], date[-2:], date[:4]])
        data = str(quantity)
        if found_value != 0:
            if messagebox.askyesno(title="Value already found for this Date",
                                   message=f"Value {found_value} was already "
                                           f"input for day {formatted_date} (mm/dd/yyyy).\n"
                                           f"Do you wish to increase this value with {quantity}??\n\n"
                                           f"You may also click the 'Change' button to update the present value."):
                data = str(float(quantity) + float(found_value))  # the increment request does not achieve this
            else:
                return

        send_pixel_endpoint = f"{PIXELA_ENDPOINT}/{self.username}/graphs/{self.graphID}"
        pixel_params = {"date": date, "quantity": data}
        headers = {"X-USER-TOKEN": self.token}

        response = requests.post(url=send_pixel_endpoint, json=pixel_params, headers=headers)
        status_msg = 'An Error Occurred'
        if response.json()['isSuccess']:
            status_msg = 'Data sent successfully'
        messagebox.showinfo(
            title=status_msg,
            message=f"Message from Pixe.la: {response.json()['message']}\n"
                    f"Value stored for this day at the moment: {data}.")

    def update_pixel(self, date, quantity):
        qnt_param = {"quantity": str(quantity)}
        update_pixel_endpoint = f"{PIXELA_ENDPOINT}/{self.username}/graphs/{self.graphID}/{date}"
        headers = {"X-USER-TOKEN": self.token}

        response = requests.put(url=update_pixel_endpoint, json=qnt_param, headers=headers)
        if response.json()['isSuccess']:
            messagebox.showinfo(title='Successfully Updated', message=response.json()['message'])
        else:
            messagebox.showerror(title='Error', message=response.json()['message'])

    def delete_pixel(self, date):
        delete_endpoint = f"{PIXELA_ENDPOINT}/{self.username}/graphs/{self.graphID}/{date}"
        headers = {"X-USER-TOKEN": self.token}

        response = requests.delete(url=delete_endpoint, headers=headers)
        if response.json()['isSuccess']:
            messagebox.showinfo(title='Successfully Deleted', message=response.json()['message'])
        else:
            messagebox.showerror(title='Error', message=response.json()['message'])

    def open_progress_page(self):
        self.get_graph_details()
        webbrowser.open(url=f'{PIXELA_ENDPOINT}/{self.username}/graphs/{self.graphID}.html')

    def create_graph(self, graphID, name, unit, color):
        graph_endpoint = f"{PIXELA_ENDPOINT}/{self.username}/graphs"
        graph_config = {
            "id": graphID,
            "name": name,
            "unit":  unit,
            "type": "float",
            "color": color
            }
        headers = {"X-USER-TOKEN": self.token}
        
        response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
        
        if response.json()['isSuccess']:
            messagebox.showinfo(title='Graph Created', message=response.json()['message'])
            return True
        else:
            messagebox.showerror(title='Error', message=response.json()['message'])
            return False

    def delete_graph(self, graphID):
        delete_endpoint = f"{PIXELA_ENDPOINT}/{self.username}/graphs/{graphID}"
        headers = {"X-USER-TOKEN": self.token}
        
        permission = messagebox.askyesno(title="Delete Graph", message="Are you sure to delete this graph?")
        if not permission:
            return
        
        response = requests.delete(url=delete_endpoint, headers=headers)
        
        if response.json()['isSuccess']:
            messagebox.showinfo(title='Graph Deleted', message=response.json()['message'])
            return True
        else:
            messagebox.showerror(title='Error', message=response.json()['message'])
            return False
