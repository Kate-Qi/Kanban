from tkinter import *
from tkinter import ttk
import tkinter

from Board import *
from Bucket import *
from database import *
from user import *
import mysql.connector

conn = mysql.connector.connect(host="localhost", port=3306, user="root", passwd="passpass")


class ProjectSelection:
    '''
    The data and visuals associated with logging into an account and
    managing Boards. Boards can be entered, created and deleted.
    '''

    def __init__(self, root):
        self.root = root # The root Tkinter object
        self.boards = [] # A list of the Boards
        self.name = None # The name of a new Bucket
        self.buckets = [] # A list of the Buckets for a new Board
        self.user_type = None

    def gen(self):
        '''
        Creates the Tkinter objects to display this screen. Returns
        an object that must be gridded to the root tkinter object.
        '''
        # A frame that stores the whole page
        mainframe = ttk.Frame(self.root)
        self.buckets = []

        # Case 1: User is not logged in and must do so
        if self.name is None:

            # A button to login
            login_btn = ttk.Button(mainframe, text="Login", command=self.create_login_window)
            login_btn.grid(column=0, row=0)

            # SQL errors with user DB - this button is disabled
            # A button to register an account
            # register_btn = ttk.Button(mainframe, text="Register", command=self.create_register_window)
            # register_btn.grid(column=0, row=1)

        # Case 2: User is already logged in
        else:
            
            # A greeting for the user
            user_greeting = ttk.Label(mainframe, text=f"Hello, {self.name}!")
            user_greeting.grid(column=0, row=0)

            # check if the user is teacher or student
            if self.user_type == 1:
                    # A button to create a new board
                add_board_btn = ttk.Button(mainframe, text="Create New Custom Board", command=self.add_board)
                add_board_btn.grid(column=1, row=1)

                add_board_btn = ttk.Button(mainframe, text="Create New Default Board", command=self.add_def_board)
                add_board_btn.grid(column=1, row=2)

            # Displays all of the already created Boards
            # see database.py for this function
            allData = getAllData()
            for i in range(len(allData)):
                boardName = allData[i][0][0]  # this is the Board name index in the allData structure
                boardName = boardName.replace("あ"," ") # replace kanji w/ whitespace
                if boardName not in self.boards:
                    self.boards.append(boardName) # append to list of boards
            # create buttons based on list above
            for i in range(len(self.boards)):
                if self.boards[i] not in boardNamesList: # if the board was not loaded from the database
                    b = ttk.Button(mainframe, text=self.boards[i], command=lambda index=i: self.enter_board(index))
                    b.grid(column=0, row=i+2) # Changes the row depending on its index
                elif (self.boards[i] in boardNamesList): # board was loaded from database
                    b = ttk.Button(mainframe, text=self.boards[i], command=lambda index=i: self.load_board(self.boards[index]))
                    b.grid(column=0, row=i+2) # Changes the row depending on its index
        # Returns the whole page
        return mainframe

    def add_def_board(self):
        new_window = Tk()

        # Prompts the user to enter board name
        name_text = ttk.Label(new_window, text="Enter name:")
        name_text.grid(column=0, row=0)

        # A text entry box to input the name
        name_entry = ttk.Entry(new_window)
        name_entry.grid(column=1, row=0)


        #print(name)
        name = name_entry.get()
        print("!!!!!!!!!!!!!!", name)

        # A button to go to the add buckets page
        continue_btn = ttk.Button(new_window, text="Continue", command=lambda: goto_main())
        continue_btn.grid(column=2, row=0)

        def goto_main():
            name = name_entry.get()
            new_window.destroy()  # Destroy the new window we created

            self.boards.append(name)  # Add the Board to the Boards list
            print(self.buckets)  # Print the buckets list, this should actually save to database
            print("**************", self.buckets, name)
            if len(self.buckets) == 0:
                print("INDEX: ", self.boards[-1])
                self.enter_board(-1)

            

            # Delete the main root window
            for widget in self.root.grid_slaves():
                widget.grid_forget()

            # Redraw the main root window
            self.gen().grid(column=0, row=0)

    def add_board(self):
        '''
        A new window that opens up to guide the user through
        creating a new Board.
        '''
        # Creates a new window
        new_window = Tk()

        # Prompts the user to enter their name
        name_text = ttk.Label(new_window, text="Enter name:")
        name_text.grid(column=0, row=0)

        # A text entry box to input the name
        name_entry = ttk.Entry(new_window)
        name_entry.grid(column=1, row=0)

        # Prompts the user to enter the number of Buckets for the Board
        num_text = ttk.Label(new_window, text="Enter number of buckets:")
        num_text.grid(column=0, row=1)

        # A text entry box for the number of Buckets
        num_entry = ttk.Entry(new_window)
        num_entry.grid(column=1, row=1)

        # A button to go to the add buckets page
        continue_btn = ttk.Button(new_window, text="Continue", command=lambda: add_buckets())
        continue_btn.grid(column=2, row=0)

        def add_buckets():
            '''
            A sub-window of the add_board window that prompts the
            user to enter the names of each of the Buckets that will
            be present in their new Board.
            '''
            # Gets the name and number of Buckets
            name = name_entry.get()
            num = num_entry.get()

            # Makes sure the name and num are not empty strings
            if len(name) > 0 and len(num) > 0:
                
                # Deletes everything on the current window
                for widget in new_window.grid_slaves():
                    widget.grid_forget()

                # Prompts the user to enter Bucket names
                instructions = ttk.Label(new_window, text="Enter bucket names in order")
                instructions.grid(column=0, row=0)

                # A text entry box to enter Bucket names
                bucket_entry = ttk.Entry(new_window)
                bucket_entry.grid(column=0, row=1)

                self.buckets = [] # A list of the new Buckets
                bucket_i = [0] # current index, wrapped in a list so it would be stored on the heap
                               # Because: Python is dumb :)

                # A button to continue to the next Bucket name
                continue_button = ttk.Button(new_window, text="Next", command=lambda: next_bucket())
                continue_button.grid(column=1, row=1)

            def next_bucket():
                '''
                A helper function for add_buckets. It advances to the
                next Bucket name until all the names have been entered.
                '''
                # Get the name of the Bucket
                bucket = bucket_entry.get()
                #print(bucket)

                # Make sure the Bucket input is not an empty string
                if len(bucket) > 0:
                    
                    self.buckets.append(Bucket(bucket, [])) # Add the new Bucket to the list
                    bucket_i[0] += 1 # Increment the current Bucket index
                    bucket_entry.delete(0, END) # Delete the text box input so the user can add another

                    # current index equals the number of buckets, we're done
                    if bucket_i[0] == int(num):
                        
                        new_window.destroy() # Destroy the new window we created

                        self.boards.append(name) # Add the Board to the Boards list
                        print(self.buckets) # Print the buckets list, this should actually save to database

                        # Delete the main root window
                        for widget in self.root.grid_slaves():
                            widget.grid_forget()

                        # Redraw the main root window
                        bins = self.buckets
                        binsList = []
                        for i in range(len(self.buckets)):
                            bins[i].title = str(bins[i].title)
                            binsList.append(bins[i].title)
                        noSpaceBoard = str(self.boards[-1]).replace(" ","あ")
                        query = "CREATE TABLE IF NOT EXISTS "+ noSpaceBoard+ " (title VARCHAR(2000),description VARCHAR(2000),"
                        for j in range(len(binsList)):
                            binName = binsList[j]
                            if j == (len(binsList)-1):
                                query += binName.replace(" ","あ")+" VARCHAR(2000))"
                            else:
                                query += binName.replace(" ","あ")+" VARCHAR(2000),"
                        createTable(conn, query)
                        self.gen().grid(column=0, row=0)

    def enter_board(self, index):
        '''
        Enters the Kanban Board that the user has selected
        '''
        # Clears the screen
        for widget in self.root.grid_slaves():
            widget.grid_forget()

        # A default set of Buckets
        if len(self.buckets) == 0:

            self.buckets = [Bucket("Not Started", []),
                       Bucket("In Progress", []),
                       Bucket("Completed", [])
                       ]

        # Create the Board
        b = Board(self.root, self.boards[index], self.buckets, self.user_type)
        # Reparent the new Buckets
        for bucket in self.buckets:
            bucket.change_parent_to(b)

        # Display the Board
        b.gen().grid(row=0, column=0)

        bins = b.buckets
        binsList = []
        # this creates a string for db query 
        for i in range(len(b.buckets)):
            bins[i].title = str(bins[i].title)
            print("AHAHAHAHAHA:",type(bins[i].title), bins[i].title, bins[i])
            binsList.append(bins[i].title)
        noSpaceBoard = str(self.boards[index]).replace(" ","あ")
        query = "CREATE TABLE IF NOT EXISTS "+ noSpaceBoard+ " (title VARCHAR(2000),description VARCHAR(2000),"
        for i in range(len(binsList)):
            binName = binsList[i]
            if i == (len(binsList)-1):
                query += binName.replace(" ","あ")+" VARCHAR(2000))"
            else:
                query += binName.replace(" ","あ")+" VARCHAR(2000),"
        #print(query)
        
        # save board in database
        createTable(conn,query)

    def load_board(self, boardTitle):
        '''
        Enters the Kanban Board that the user has selected
        '''
        # Clears the screen
        for widget in self.root.grid_slaves():
            widget.grid_forget()

        tempIndex = boardNamesList.index(boardTitle)

        binList = []
        for bucket in range(len(allData[tempIndex][0])):
            if (bucket != 0) and (bucket != 1)and (bucket != 2):
                binList.append(allData[tempIndex][0][bucket].replace("あ", " "))
        
        
        # Create the Board
        b = Board(self.root, boardTitle,binList, self.user_type)


        cards = []
        for card in range(len(allData[tempIndex])):
            if card != 0:
                cc = Card(allData[tempIndex][card][0],allData[tempIndex][card][1])
                cards.append(cc)

        for i in range(len(binList)):
            bb = Bucket(binList[i], [])
            binList[i] = bb
        
        for card in range(len(cards)):
            temp = card+1
            c = cards[card]
            binLoc = allData[tempIndex][temp].index("1")
            binList[binLoc-2].add_card(c)

        # Reparent the new Buckets
        for bucket in binList:
            bucket.change_parent_to(b)

        # Display the Board
        b.gen().grid(row=0, column=0)


    def create_login_window(self):
        new_window = Tk()
        new_window.title("Kanban")

        window_frame = ttk.Frame(new_window, padding="4 10 4 10")

        user_type_text = ttk.Label(window_frame, text="Select your user type:")
        user_type_text.grid(column=0, row=0)

        user_type = IntVar(new_window)  # need to give the window as an arg for this to work
        student_btn = ttk.Radiobutton(window_frame, text="Student", variable=user_type, value=0, command= lambda: studentval())
        student_btn.grid(column=1, row=0)
        instructor_btn = ttk.Radiobutton(window_frame, text="Instructor", variable=user_type, value=1, command = lambda: instructorval())
        instructor_btn.grid(column=2, row=0)

        def studentval():
            self.user_type = 0

        def instructorval():
            self.user_type = 1

        name_text = ttk.Label(window_frame, text="Enter Name:")
        name_text.grid(column=0, row=1)

        name = StringVar() 
        name_input = ttk.Entry(window_frame, textvariable=name)
        name_input.grid(column=1, row=1)

        password_text = ttk.Label(window_frame, text="Enter Password:")
        password_text.grid(column=0, row=2)

        password = StringVar() 
        password_input = ttk.Entry(window_frame, textvariable=password)
        password_input.grid(column=1, row=2)

        login_button = ttk.Button(window_frame,
                                  text="Sign in",
                                  command=lambda: self._login(name_input.get(), password_input.get(), new_window)
                                  )
        login_button.grid(column=0, row=3)

        window_frame.grid(column=0, row=0)

        new_window.mainloop()

    def _login(self, name: str, password: str, new_window):
        self.name = name
        # Need to login here
        new_window.destroy()
        for widget in self.root.grid_slaves():
            widget.grid_forget()

        self.gen().grid(column=0, row=0)
    
    def create_register_window(self):
        new_window = Tk()
        new_window.title("KFC Registration")

        window_frame = ttk.Frame(new_window, padding = "4 10 4 10")

        name_text = ttk.Label(window_frame, text="Enter Name:")
        name_text.grid(column=0, row=0)

        name = StringVar() 
        name_input = ttk.Entry(window_frame, textvariable=name)
        name_input.grid(column=1, row=0)

        password_text = ttk.Label(window_frame, text="Enter Password:")
        password_text.grid(column=0, row=1)

        password = StringVar() 
        password_input = ttk.Entry(window_frame, textvariable=password)
        password_input.grid(column=1, row=1)

        user_type_text = ttk.Label(window_frame, text="Select your user type:")
        user_type_text.grid(column=0, row=2)

        user_type = IntVar(new_window) # need to give the window as an arg for this to work
        student_btn = ttk.Radiobutton(window_frame, text = "Student", variable = user_type, value = 1)
        student_btn.grid(column = 1, row = 2)
        instructor_btn = ttk.Radiobutton(window_frame, text = "Instructor", variable = user_type, value = 0)
        instructor_btn.grid(column = 2, row = 2)


        register_button = ttk.Button(window_frame,
                                  text="Register",
                                  command=lambda: self._register(name_input.get(), password_input.get(), user_type.get(), new_window)
                                  )
        register_button.grid(column=0, row=3)

        window_frame.grid(column=0, row=0)

        new_window.mainloop()        

    def _register(self, name: str, password: str, user_type: int, new_window):
        self.name = name
        # check un and pw for whitepsace
        if ((' ' in name) or (' ' in password)):
            err = Toplevel(new_window)
            err.geometry("400x100")
            err.title("Registration Error")
            #Create a label in Toplevel window
            errLab = Label(err, text= "Error: you cannot use spaces in a username or password").pack()
            
        else:
            # setup user DB and users table
            createUserDB(conn)
            createUsersTable(conn)  
            # query DB to check for duplicate account(s)
            if checkForUser(conn, (name, password, user_type)):
                # add account to DB
                insertUser(conn, (name, password, user_type))
                new_window.destroy()
                for widget in self.root.grid_slaves():
                    widget.grid_forget()

                self.gen().grid(column=0, row=0)
