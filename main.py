import kivy
from kivymd.app import MDApp
from kivy.app import App
from kivymd.uix.screen import Screen
# from kivymd.uix.scrollview import ScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer, MDNavigationDrawerMenu, \
    MDNavigationDrawerHeader
from kivymd.uix.list import OneLineListItem, MDList, ThreeLineIconListItem, TwoLineIconListItem, ThreeLineListItem, \
    TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.uix.popup import Popup
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivy.clock import Clock
from plyer import filechooser
import os
import threading
from datetime import datetime, timedelta
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
import firebase_admin
from firebase_admin import credentials, db, storage
import requests
from io import BytesIO
from kivy.core.image import Image as CoreImage
from google.cloud import storage as gcs_storage

# Initialize Firebase
cred_path = 'C:\\Eswar\\TodoList\\todolistkivyapp-firebase-adminsdk-2ggnt-9d36358bd4.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://todolistkivyapp-default-rtdb.firebaseio.com/',
    'storageBucket': 'todolistkivyapp.appspot.com'
})

# helpers
screen_helper = '''
ScreenManager:
    LoginScreen:
    SignupScreen:
    ProfileScreen:
    AddTaskScreen:

<LoginScreen>:
    name: 'Login Page'
    MDTextField:
        id: login_username
        hint_text: 'Enter Username'
        helper_text: 'please enter Username'
        helper_text_mode: 'on_focus'
        icon_left: 'account-circle'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.7}
        size_hint_x: None
        width: 300
    MDTextField:
        id: login_password
        hint_text: 'Enter Password'
        helper_text: 'Enter Password'
        helper_text_mode: 'on_focus'
        icon_left: 'account-lock'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.6}
        size_hint_x: None
        width: 300
        password: True
    MDRectangleFlatButton:
        text: 'Login'
        pos_hint: {'center_x' : 0.3, 'center_y' : 0.5}
        on_press: root.verify_login()
    MDRectangleFlatButton:
        text: 'SignUp'
        pos_hint: {'center_x' : 0.55, 'center_y' : 0.5}
        on_press: root.manager.current='Signup Page'

<SignupScreen>:
    name: 'Signup Page'
    MDTextField:
        id: signup_username
        hint_text: 'Enter Username'
        helper_text: 'please enter Username'
        helper_text_mode: 'on_focus'
        icon_left: 'account-circle'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.8}
        size_hint_x: None
        width: 300
    MDTextField:
        id: signup_password
        hint_text: 'Enter Password'
        helper_text: 'Enter Password'
        helper_text_mode: 'on_focus'
        icon_left: 'account-lock'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.7}
        size_hint_x: None
        width: 300
        password: True
    MDTextField:
        id: signup_fullname
        hint_text: 'Enter Full Name'
        helper_text: 'please enter Full Name'
        helper_text_mode: 'on_focus'
        icon_left: 'account'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.6}
        size_hint_x: None
        width: 300
    MDTextField:
        id: signup_dob
        hint_text: 'Date Of Birth (YYYY-MM-DD)'
        helper_text: 'Enter DOB '
        helper_text_mode: 'on_focus'
        icon_left: 'calendar'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.5}
        size_hint_x: None
        width: 300
        readonly: True
        on_focus: if self.focus: root.show_date_picker()
    MDTextField:
        id: signup_email
        hint_text: 'Enter Email'
        helper_text: 'please enter Email'
        helper_text_mode: 'on_focus'
        icon_left: 'email'
        icon_left_color: app.theme_cls.primary_color
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.4}
        size_hint_x: None
        width: 300
    Image:
        id: signup_profile_pic
        source: ''
        pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        size_hint: (None, None)
        size: (100, 100)
    MDRectangleFlatButton:
        text: 'Choose Profile Pic'
        pos_hint: {'center_x' : 0.5, 'center_y' : 0.2}
        on_press: root.select_file()
    MDRectangleFlatButton:
        text: 'Sign Up'
        pos_hint: {'center_x' : 0.35, 'center_y' : 0.1}
        on_press: root.verify_signup()
    MDRectangleFlatButton:
        text: 'Login'
        pos_hint: {'center_x' : 0.65, 'center_y' : 0.1}
        on_press: root.go_to_login()

<ProfileScreen>:
    name: 'Profile Page'
    MDNavigationLayout:
        ScreenManager:
            Screen:
                BoxLayout:
                    orientation: 'vertical'
                    MDTopAppBar:
                        id: toolbar
                        title: "Hi, User"
                        left_action_items: [['account-circle', lambda x: nav_drawer.set_state('toggle')]]
                        elevation: 10
                    MDBottomNavigation:
                        id: bottom_navigation
                        text_color_active: app.theme_cls.primary_color
                        MDBottomNavigationItem:
                            name: "Ongoing"
                            text: "Ongoing"
                            icon: 'progress-check'
                            on_tab_press: root.switch_tab('Ongoing')
                            BoxLayout:
                                orientation: 'vertical'
                                MDLabel:
                                    text: "Ongoing Tasks"
                                    font_style: "H5"
                                    halign: 'center'
                                    size_hint_y: None
                                    height: self.texture_size[1]
                                ScrollView:
                                    bar_width: 0
                                    MDList:
                                        id: tasks_layout
                                        padding: dp(10)
                                        spacing: dp(10)
                                        size_hint_y: None
                                        height: self.minimum_height  # Adjust the height dynamically
                                        pos_hint: {'top': 1}
                                        adaptive_height: True
                        MDBottomNavigationItem:
                            name: "Add Task"
                            text: "Add Task"
                            icon: 'plus'
                            on_tab_press: root.manager.current = 'Add Task Page'
                            BoxLayout:
                                orientation: 'vertical'
                                MDLabel:
                                    text: "Add Task"
                                    font_style: "H5"
                                    halign: 'center'
                                    size_hint_y: None
                                    height: self.texture_size[1]
                        MDBottomNavigationItem:
                            name: "Completed"
                            text: "Completed"
                            icon: 'check-circle'
                            on_tab_press: root.switch_tab('Completed')
                            BoxLayout:
                                orientation: 'vertical'
                                MDLabel:
                                    text: "Completed Tasks"
                                    font_style: "H5"
                                    halign: 'center'
                                    size_hint_y: None
                                    height: self.texture_size[1]
                                ScrollView:
                                    bar_width: 0
                                    MDList:
                                        id: completed_tasks_layout
                                        padding: dp(10)
                                        spacing: dp(10)
                                        size_hint_y: None
                                        height: self.minimum_height  # Adjust the height dynamically
                                        pos_hint: {'top': 1}
                                        adaptive_height: True
        MDNavigationDrawer:
            id: nav_drawer
            BoxLayout:
                orientation: 'vertical'
                spacing: '8dp'
                padding: '8dp'
                Image:
                    id: profile_pic
                    source: 'profile_placeholder.png'
                    size_hint: (None, None)
                    size: (300, 200)
                    pos_hint: {'center_x': 0.5}
                MDLabel:
                    text: "User Name"
                    id: profile_name
                    font_style: 'Button'
                    size_hint_y: None
                    height: self.texture_size[1]
                ScrollView:
                    MDList:
                        OneLineListItem:
                            text: 'Profile'
                            on_press:
                                nav_drawer.set_state('close')
                        OneLineListItem:
                            text: 'Logout'
                            on_press: app.logout()

<AddTaskScreen>:
    name: 'Add Task Page'
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        MDTextField:
            id: task_name
            hint_text: 'Enter Task Name'
            icon_left: 'format-list-bulleted'
            icon_left_color: app.theme_cls.primary_color
        MDTextField:
            id: task_description
            hint_text: 'Enter Task Description'
            icon_left: 'note-text'
            icon_left_color: app.theme_cls.primary_color
        MDTextField:
            id: task_deadline_date
            hint_text: 'Enter Deadline (YYYY-MM-DD)'
            icon_left: 'calendar'
            icon_left_color: app.theme_cls.primary_color
            readonly: True
            on_focus: if self.focus: root.show_date_picker()
        MDTextField:
            id: task_deadline_time
            hint_text: 'Enter Deadline Time (HH:MM:SS)'
            icon_left: 'clock'
            icon_left_color: app.theme_cls.primary_color
            readonly: True
            on_focus: if self.focus: root.show_time_picker()
        MDRaisedButton:
            text: 'Add Task'
            on_press: root.add_task()
        MDRaisedButton:
            text: "Cancel"
            on_release: app.root.get_screen('Add Task Page').cancel_add_task()

'''


class LoginScreen(Screen):
    def verify_login(self):
        username = self.ids.login_username.text
        password = self.ids.login_password.text

        ref = db.reference('/users')
        users = ref.order_by_child('username').equal_to(username).get()

        if users:
            for key, value in users.items():
                if value['password'] == password:
                    print('Login Successful!')
                    self.ids.login_username.text = ''
                    self.ids.login_password.text = ''
                    self.manager.current = 'Profile Page'
                    app = App.get_running_app()
                    app.user_key = key  # Store the user's key for further reference
                    app.load_profile()  # Load profile data
                    return

        print('Login Failed')


class SignupScreen(Screen):
    def show_date_picker(self):
        date_dialog = MDDatePicker(
            title="Pick a Date",
            min_year=1900,
            max_year=datetime.now().year,
        )
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.ids.signup_dob.text = value.strftime("%Y-%m-%d")

    def select_file(self):
        filechooser.open_file(on_selection=self.on_file_selected)

    def on_file_selected(self, selection):
        if selection:
            self.ids.signup_profile_pic.source = selection[0]
            self.profile_pic_path = selection[0]

    def verify_signup(self):
        username = self.ids.signup_username.text
        password = self.ids.signup_password.text
        fullname = self.ids.signup_fullname.text
        dob = self.ids.signup_dob.text
        email = self.ids.signup_email.text

        if not username or not password or not fullname or not dob or not email:
            print("Please fill all fields.")
            return

        ref = db.reference('/users')
        users = ref.order_by_child('username').equal_to(username).get()

        if users:
            print('Username already exists')
            return

        # Save user data
        new_user_ref = ref.push({
            'username': username,
            'password': password,
            'fullname': fullname,
            'dob': dob,
            'email': email,
        })

        if hasattr(self, 'profile_pic_path'):
            bucket = storage.bucket()
            blob = bucket.blob(f"profile_pics/{new_user_ref.key}.png")
            blob.upload_from_filename(self.profile_pic_path)
            print(f"Profile picture uploaded to {blob.public_url}")

        print('User signed up successfully!')
        self.manager.current = 'Login Page'

    def go_to_login(self):
        self.manager.current = 'Login Page'


class ProfileScreen(Screen):

    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.load_ongoing_tasks, 10)
    def on_enter(self):
        # This method is called when the screen is about to be displayed
        self.load_ongoing_tasks()

    def switch_tab(self, tab_name):
        if tab_name == 'Ongoing':
            self.load_ongoing_tasks()
        elif tab_name == 'Completed':
            self.load_completed_tasks()

    def load_ongoing_tasks(self, *args):
        tasks_layout = self.ids.tasks_layout
        tasks_layout.clear_widgets()
        app = App.get_running_app()
        user_key = app.user_key

        if user_key:
            ref = db.reference(f'/tasks/{user_key}')
            tasks = ref.order_by_child('status').equal_to('ongoing').get()

            if tasks:
                for key, task in tasks.items():
                    due_text = self.compute_due_text(task)
                    item = ThreeLineListItem(
                        text=task['name'],
                        secondary_text=task['description'],
                        tertiary_text=due_text
                    )
                    tasks_layout.add_widget(item)
            else:
                tasks_layout.add_widget(Label(text="No ongoing tasks."))


    def load_completed_tasks(self):
        completed_tasks_layout = self.ids.completed_tasks_layout
        completed_tasks_layout.clear_widgets()
        app = App.get_running_app()
        user_key = app.user_key

        if user_key:
            ref = db.reference(f'/tasks/{user_key}')
            tasks = ref.order_by_child('status').equal_to('completed').get()

            if tasks:
                for key, task in tasks.items():
                    item = TwoLineListItem(text=task['name'], secondary_text=task['description'])
                    completed_tasks_layout.add_widget(item)
            else:

                completed_tasks_layout.add_widget(Label(text="No completed tasks."))

    def compute_due_text(self, task):
        if 'deadline' in task:
            due_date_str = task['deadline']
            completion_time_str = task.get('completion_time', None)  # Get completion time if available

            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()

                if completion_time_str:
                    completion_time = datetime.strptime(completion_time_str, "%Y-%m-%d %H:%M:%S")
                    if completion_time <= due_date:
                        due_text = "Completed on time"
                    else:
                        due_text = "Completed after deadline"
                else:
                    if now <= due_date:
                        time_remaining = due_date - now
                        days = time_remaining.days
                        hours, remainder = divmod(time_remaining.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        due_text = f"Due in {days}d {hours}h {minutes}m"
                    else:
                        due_text = "Past due"

            except ValueError:
                due_text = "Invalid date format"
        else:
            due_text = "No due date"

        return due_text


class AddTaskScreen(Screen):
    def show_date_picker(self):
        date_dialog = MDDatePicker(
            title="Pick a Date",
            min_year=2020,
            max_year=2050,
        )
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.ids.task_deadline_date.text = value.strftime("%Y-%m-%d")
        self.show_time_picker()

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.on_time_selected)
        time_dialog.open()

    def on_time_selected(self, instance, time):
        self.ids.task_deadline_time.text = time.strftime("%H:%M:%S")

    def add_task(self):
        task_name = self.ids.task_name.text
        task_description = self.ids.task_description.text
        task_deadline_date = self.ids.task_deadline_date.text
        task_deadline_time = self.ids.task_deadline_time.text

        if not task_name or not task_description or not task_deadline_date or not task_deadline_time:
            print("Please fill all fields.")
            return

        # Combine date and time into a single datetime object
        try:
            task_deadline = datetime.strptime(f"{task_deadline_date} {task_deadline_time}", '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("Invalid date or time format. Please use YYYY-MM-DD and HH:MM:SS.")
            return

        # Determine initial task status based on current date and time
        if task_deadline < datetime.now():
            initial_status = 'completed'
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            initial_status = 'ongoing'
            completion_time = None

        app = App.get_running_app()
        ref = db.reference(f'/tasks/{app.user_key}')
        new_task_data = {
            'name': task_name,
            'description': task_description,
            'deadline': task_deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'status': initial_status,
            'completion_time': completion_time
        }
        new_task_ref = ref.push(new_task_data)

        print("Task added successfully!")

        # Reset fields after adding task
        self.ids.task_name.text = ''
        self.ids.task_description.text = ''
        self.ids.task_deadline_date.text = ''
        self.ids.task_deadline_time.text = ''

        # Switch to 'Profile Page' and reload ongoing tasks
        self.manager.current = 'Profile Page'
        self.load_ongoing_tasks()

        # Optional: Implement automatic status update based on current date and time
        self.schedule_status_update(new_task_ref.key, task_deadline)

    def schedule_status_update(self, task_key, deadline):
        # Calculate initial delay before first check (if deadline is in the future)
        initial_delay = (deadline - datetime.now()).total_seconds()

        # Schedule a thread to run the update logic after initial_delay
        timer = threading.Timer(initial_delay, self.update_task_status, args=(task_key,))
        timer.start()

    def update_task_status(self, task_key):
        # Fetch the task from Firebase Realtime Database
        app = App.get_running_app()
        task_ref = db.reference(f'/tasks/{app.user_key}/{task_key}')
        task = task_ref.get()

        if not task:
            print(f"Task with key '{task_key}' not found.")
            return

        deadline = datetime.strptime(task['deadline'], '%Y-%m-%d %H:%M:%S')
        current_status = task['status']

        # Check if the deadline has passed
        if deadline < datetime.now() and current_status == 'ongoing':
            # Update the task status to 'completed' and set the completion time
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            task_ref.update({
                'status': 'completed',
                'completion_time': completion_time
            })
            print(f"Task '{task['name']}' marked as completed with completion time {completion_time}.")
        else:
            print(f"No action needed for task '{task['name']}'.")

    def load_ongoing_tasks(self):
        # Implement your logic to load ongoing tasks here
        pass

    def cancel_add_task(self):
        # Reset fields and switch to 'Profile Page'
        self.ids.task_name.text = ''
        self.ids.task_description.text = ''
        self.ids.task_deadline_date.text = ''
        self.ids.task_deadline_time.text = ''
        self.manager.current = 'Profile Page'
        self.load_ongoing_tasks()

class MainApp(MDApp):
    user_key = None

    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        return Builder.load_string(screen_helper)

    def load_profile(self):
        ref = db.reference(f'/users/{self.user_key}')
        user_data = ref.get()

        profile_screen = self.root.get_screen('Profile Page')
        profile_screen.ids.toolbar.title = f"Hi, {user_data['fullname']}"
        profile_screen.ids.profile_name.text = user_data['fullname']

        # Load profile picture
        bucket = storage.bucket()
        blob = bucket.blob(f"profile_pics/{self.user_key}.png")

        if blob.exists():
            image_url = blob.generate_signed_url(timedelta(seconds=300), method='GET')
            print(image_url)
            image_dir = 'profile_pic'

            # Create the directory if it doesn't exist
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

            # Path to save the image
            image_path = os.path.join(image_dir, 'profile.png')

            # Download the image
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)

            profile_screen.ids.profile_pic.source = image_path
            profile_screen.ids.profile_pic.reload()

    def logout(self):
        self.user_key = None

        self.root.current = 'Login Page'


if __name__ == '__main__':
    MainApp().run()
