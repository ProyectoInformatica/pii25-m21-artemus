import tkinter as tk

# Example Tinker Code

root = tk.Tk()
root.title("Hola, Mundo")
root.geometry("300x200")

label = tk.Label(root, text="¡Bienvenido a Tkinter!")
label.pack(pady=20)

root.mainloop()
