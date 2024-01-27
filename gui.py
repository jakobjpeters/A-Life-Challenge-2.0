import tkinter as tk


class App:
    def __init__(self, root):
        self.root = root
        root.title("A-Life Challenge")

        # window size
        width = 800
        height = 600
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # create frames for each screen
        self.main_frame = tk.Frame(root, width=800, height=600, bg='#2f2f2f')
        self.button_frame = tk.Frame(
            self.main_frame, width=250, height=200, bg='#3E3E3E')

        # dynamic coordinates
        canvas_center_x = width / 2
        canvas_center_y = height / 2

        # buttons on the button frame
        start_button = tk.Button(self.button_frame, text="Start", command=self.start_button_command,
                                 width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        start_button.grid(row=0, column=0, pady=10, padx=10)

        load_button = tk.Button(self.button_frame, text="Load", command=self.load_button_command,
                                width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        load_button.grid(row=1, column=0, pady=10)

        about_button = tk.Button(self.button_frame, text="About", command=self.about_button_command,
                                 width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        about_button.grid(row=2, column=0, pady=10)

        # label box
        self.label = tk.Label(self.main_frame, text="This is a little blurb about the simulation", font=('Times', 14),
                              fg="#000000")
        self.label.place(x=canvas_center_x - 167, y=20, width=335, height=93)

        # show the initial screen
        self.show_screen(self.button_frame)

    def show_screen(self, screen_frame):
        # hide other screens and show requested one
        self.button_frame.pack_forget()
        self.main_frame.pack_forget()

        screen_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def start_button_command(self):
        # new frame for the start screen
        start_screen_frame = tk.Frame(
            self.main_frame, width=800, height=600, bg='#2f2f2f')
        tk.Label(start_screen_frame, text="Welcome to the Start screen!", font=('Times', 14),
                 fg="#FFFFFF", bg='#2f2f2f').pack(pady=50)

        # show the new frame
        self.show_screen(start_screen_frame)

    def load_button_command(self):
        print("Load button command")

    def about_button_command(self):
        print("About button command")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
