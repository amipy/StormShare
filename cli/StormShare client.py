import requests, simplejson,tkinter, tkinter.ttk, json
class StormShare(tkinter.ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.login()
        self.loginSuccess=False
    def login(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.master.title("Login")
        self.username=tkinter.StringVar()
        self.password=tkinter.StringVar()
        self.userDesc=tkinter.ttk.Label(self, text="Username")
        self.userBox=tkinter.ttk.Entry(self, textvariable=self.username)
        self.userDesc.pack()
        self.userBox.pack()
        self.passDesc = tkinter.ttk.Label(self, text="Password")
        self.passBox=tkinter.ttk.Entry(self, textvariable=self.password)
        self.passDesc.pack()
        self.passBox.pack()
        self.submitButton=tkinter.ttk.Button(self, text="Login", command=loginCall)
        self.submitButton.pack(side="bottom")
        self.lgStat = tkinter.ttk.Label(self)
        self.lgStat.pack(side="bottom")

def enkode(string):
    lenEnc=len(string)
    newStorng=""
    for ind,i in enumerate(string):
        newStorng+=chr((ord(i)+lenEnc*ind)%256)
    encoded=newStorng[::-1]
    return encoded
with open("config.json") as cfg:
    serverAddress=json.load(cfg)["addr"]
#serverAddress="http://10.0.0.118:5000/"
#print(serverAddress)
headers={
    "content-type":"application/json",
    "accept":"*/*"
}

authValid=False
def sendAPI(address, headers, data, route):
    r = requests.get(f"{address}{route}", headers=headers, data=simplejson.dumps(data).encode('utf-8'))
    if r.status_code==404:
        print("Failed to connect to server.")
    if r.status_code==500:
        print("Server error. A ticket has been logged.")
    return r.json(), r
def loginCall():
    username=app.username.get()
    password=app.password.get()
    response, _ = sendAPI(serverAddress, headers, {"auth":[username,enkode(password)]}, "auths/validate")
    authValid = response["status"]
    print(authValid)
    if authValid:
        app.lgStat.config(text="Login successfull")
    if not authValid:
        app.lgStat.config(text="Incorrect login")
    app.loginSuccess=True

root=tkinter.Tk()
app = StormShare(master=root)
root.mainloop()