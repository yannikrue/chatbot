import tkinter as tk

from chatbot import chatbot_response

class ConsoleText(tk.Text):

    def __init__(self, master=None, **kw):
        tk.Text.__init__(self, master, **kw)
        self.insert('1.0', '>>> ') # first prompt
        # create input mark
        self.mark_set('input', 'insert')
        self.mark_gravity('input', 'left')
        # create proxy
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        # binding to Enter key
        self.bind("<Return>", self.enter)


    def _proxy(self, *args):
        largs = list(args)

        if args[0] == 'insert':
            if self.compare('insert', '<', 'input'):
                # move insertion cursor to the editable part
                self.mark_set('insert', 'end')  # you can change 'end' with 'input'
        elif args[0] == "delete":
            if self.compare(largs[1], '<', 'input'):
                if len(largs) == 2:
                    return # don't delete anything
                largs[1] = 'input'  # move deletion start at 'input'
        result = self.tk.call((self._orig,) + tuple(largs))
        return result

    def enter(self, event):
        command = self.get('input', 'end')
        # execute code
        command.replace(">>>", "")
        print(command)
        res = chatbot_response(command)
        # display result and next promp
        self.insert('end', '\n{}\n\n>>> '.format(res))
        # move input mark
        self.mark_set('input', 'insert')

        self.see('end')
        return "break" # don't execute class method that inserts a newline

root = tk.Tk()
tfield = ConsoleText(root, bg='black', fg='green', insertbackground='white')
tfield.pack()
root.mainloop()