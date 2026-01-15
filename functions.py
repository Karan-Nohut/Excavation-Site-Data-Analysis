def center_window(window): #Method to ensure windows appear in the middle of the users screen by finding the users screen size and the app size and placing it in the middle
    x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
    y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
    window.geometry(f'{window.winfo_width()}x{window.winfo_height()}+{x}+{y}')