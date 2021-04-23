import io
import os
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO

import xmltodict, json
from flask import Flask, render_template
import pickle

tgt = r"C:\Users\alexi\AppData\Roaming\Stormworks\data\vehicles\airfuselage.xml"
app = Flask(__name__)
with open(tgt, "r") as flie:
    vehicleString = flie.read()

#auths = {"alexi": {"pass": "password", "projs": [1]}}
# Channel structure:
# channelid:{name:channelname,branches:{branchname:[{data:data, commit:commit}]}}

#chans = {
#    1: {"name": "ungabunk", "branches": {"main": [{"data": "ubudfuwoeub", "commit": "Eat feef"}]}, "shares": ["alexi"],
#        "owner": "alexi"}}


# print(vehicleString)
# endpoints

# auth:
# validateAuth: returns wether the auth sent is valid [DONE]
# Sent: {"auth":["USER","PASS"]}
# Recieved: {"status":"STATUS"}

# makeAuth: Creates new auth credentials and thus a user [DONE]
# Sent: {"auth":["USER","PASS"]}
# Recieved: {"status":"STATUS"}

# delAuth: deletes auth creds [DONE]
# Sent: {"auth":["USER","PASS"]}
# Recieved: {"status":"STATUS"}


# channels:
# getChannels: returns names and ids of channels for a user [DONE]
# Sent: {"auth":["USER","PASS"]}
# Recieved: {"channels":{[channelid:channel]}}

# makeChannel: creates a new channel using auth [DONE]
# Sent: {"auth":["USER","PASS"], "channelname":"NAME", "shared":{["USER"]}}
# Recieved: {"id":"CHANNELID"}

# shareChannel: shares a channel with another user
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID", "shared":"USER"} [DONE]
# Recieved: {}

# unshareChannel: unshares a channel with another user
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID", "shared":{["USER"]}} [DONE]
# Recieved: {}

# getChannelShares: returns all people a channel is shared with [DONE]
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID"}
# Recieved: {["USER"]}


# branches:
# push: pushes supplied data into selected branch on selected channel
# Sent: {"channel": "CHANNELID","auth":["USER","PASS"], "branch":"BRANCH", "commit", "MESSAGE", "data":"DATA"}
# Recieved: {"channel":"CHANNEL", "branch":"BRANCH", "data":"DATA"}

# pull: pulls data from requested branch
# Sent: {"channel": "CHANNELID","auth":["USER","PASS"], "branch":"BRANCH", "verAgo":"ROLLBACKS"}
# Recieved: {"commit":"MESSAGE", "data":"DATA"}

# pullMessage: pulls commit message from selected branch [DONE]
# Sent: {"channel": "CHANNELID","auth":["USER","PASS"], "branch":"BRANCH", "verAgo":"ROLLBACKS"}
# Recieved: {"commit":"MESSAGE"}

# getBranches: returns names of branches in the channel [DONE]
# Sent: {"auth":["USER","PASS"], "channel": "CHANNELID"}
# Recieved: {"branches":{[branches:branchnames]}}

# makeBranch: makes a new branch [DONE]
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID", "branchname":"NAME"}
# Recieved: {}

# removeBranch: deletes a branch, and returns deleted data [DONE]
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID", "branchname":"NAME"}
# Recieved: {"data":"DATA"}

def unpack():
    with open("chans.dat", mode="rb") as cFile: chans = pickle.load(cFile)
    with open("auths.dat", mode="rb") as aFile: auths = pickle.load(aFile)
    return chans, auths


def pack(chans, auths):
    with open("chans.dat", mode="wb") as cFile: pickle.dump(chans, cFile)
    with open("auths.dat", mode="wb") as aFile: pickle.dump(auths, aFile)


from flask import request


@app.route("/school/post", methods=['POST'])
def post():
    return  {"output":request.data}

#@app.route("/school/path")
def path():
    path = r"C:\Users\alexi\PycharmProjects\schoolpathfinder\project\test_for_server.py"
    # data = request.get_json()
    proc = subprocess.Popen(['python', path, "1 2 3"], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    return render_template("template.html", sum=output) # {"output":output}

@app.route("/auths/validate", methods=['POST'])
def validate():
    chans, auths = unpack()
    print('1', request.data)
    auth = request.get_json()
    print(auth)
    print(request.get_json())
    print("vaa")
    user, passw = auth["auth"]
    # print(auth, type(auth))
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            pack(chans, auths)
            return {"status": True, "last-login":"123"}
    return {"status": False}


@app.route("/auths/make", methods = ['POST'])
def makeAuth():
    chans, auths = unpack()
    auth = request.get_json()
    user, passw = auth["auth"]
    if user in auths.keys():
        return {"status": False}
    auths.update({user: {"pass": passw, "projs": []}})
    pack(chans, auths)
    return {"status": True}


@app.route("/auths/del", methods = ['DELETE'])
def delAuth():
    chans, auths = unpack()
    auth = request.get_json()
    user, passw = auth["auth"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            shared_channels = auths[user]["projs"]
            for i in shared_channels:
                chans[i]["shares"].remove(user)
            del auths[user]
            pack(chans, auths)
            return {"status": True}
    return {"status": False}


@app.route("/channels/get")
def getChannels():
    chans, auths = unpack()
    print(chans)
    auth = request.get_json()
    user, passw = auth["auth"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            # {"channels": {[channelid: channel]}}
            shared_channels = auths[user]["projs"]
            channels = {}
            for i in shared_channels:
                channel_id = i
                channel_name = chans[i]["name"]
                channels.update({channel_id: channel_name})
            pack(chans, auths)
            return channels
    return {"status": False}


@app.route("/channels/share", methods = ['POST'])
def shareChannel():
    chans, auths = unpack()
    req = request.get_json()
    # {"auth": ["USER", "PASS"], "channelid": "CHANNELID", "share": "USER"}
    channelid = req["channelid"]
    sharing = req["share"]
    user, passw = req["auth"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if chans[channelid]["owner"] == user:
                if channelid in chans.keys():
                    if sharing in auths.keys():
                        chans[channelid]["shares"].append(sharing)
                        auths[sharing]["projs"].append(channelid)
                        pack(chans, auths)
                        return {"status": True}
    return {"status": False}


@app.route("/channels/getShares")
def getShares():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    shares = chans[channelid]["shares"]
                    pack(chans, auths)
                    return {"shares": shares}
    return {"status": False}


@app.route("/channels/unshare", methods = ['POST'])
def unshare():
    chans, auths = unpack()
    req = request.get_json()
    # {"auth": ["USER", "PASS"], "channelid": "CHANNELID", "share": "USER"}
    channelid = req["channelid"]
    sharing = req["share"]
    user, passw = req["auth"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if chans[channelid]["owner"] == user:
                if channelid in chans.keys():
                    if sharing in auths.keys():
                        chans[channelid]["shares"].remove(sharing)
                        auths[sharing]["projs"].remove(channelid)
                        pack(chans, auths)
                        return {"status": True}
    return {"status": False}


@app.route("/channels/make", methods = ['POST'])
def makeChannel():
    chans, auths = unpack()
    req = request.get_json()
    # {"auth": ["USER", "PASS"], }
    # channelid = req["channelid"]
    channame = req["name"]
    user, passw = req["auth"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            newid = max(chans.keys()) + 1
            # {"name":"ungabunk", "branches":{"main":[{"data":"ubudfuwoeub", "commit":"Eat feef"}]}, "shares":["alexi"], "owner":"alexi"}
            newChannel = {"name": channame, "branches": {}, "shares": [user], "owner": user}
            # print(newid, newChannel)
            chans.update({newid: newChannel})
            auths[user]["projs"].append(newid)
            # print(chans)
            pack(chans, auths)
            return {"status": True}
    return {"status": False}


# getBranches: returns names of branches in the channel
# Sent: {"auth":["USER","PASS"], "channel": "CHANNELID"}
# Recieved: {"branches":{[branches:branchnames]}}


@app.route("/branches/get")
def getBranches():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    names = list(chans[channelid]["branches"].keys())
                    pack(chans, auths)
                    return {"branches": names}
    return {"status": False}


# makeBranch: makes a new branch
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID", "branchname":"NAME"}
# Recieved: {}
@app.route("/branches/make", methods = ['POST'])
def makeBranch():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    name = req["branch"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if not name in chans[channelid]["branches"].keys():
                        chans[channelid]["branches"].update({name: [{"data": "", "commit": ""}]})
                        pack(chans, auths)
                        return {"status": True}
    return {"status": False}


# removeBranch: deletes a branch, and returns deleted data
# Sent: {"auth":["USER","PASS"], "channelid":"CHANNELID", "branchname":"NAME"}
# Recieved: {"data":"DATA"}
@app.route("/branches/del", methods = ['DELETE'])
def delBranch():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    name = req["branch"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if name in chans[channelid]["branches"].keys():
                        branchdata = chans[channelid]["branches"][name]
                        # chans[channelid]["branches"].remove(name)
                        del chans[channelid]["branches"][name]
                        pack(chans, auths)
                        return {"data": branchdata}
    return {"status": False}


# pullMessage: pulls commit message from selected branch
# Sent: {"channel": "CHANNELID","auth":["USER","PASS"], "branch":"BRANCH", "verAgo":"ROLLBACKS"}
# Recieved: {"commit":"MESSAGE"}
@app.route("/branches/getMaxRollbacks")
def getMaxRollbacks():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    # branch = req["branch"]
    name = req["branch"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if name in chans[channelid]["branches"].keys():
                        pack(chans, auths)
                        return {"rollbacks": len(chans[channelid]["branches"]) - 1}
    return {"status": False}


@app.route("/branches/getCommit")
def getCommit():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["branch"]
    # branch = req["branch"]
    name = req["name"]
    rollbacks = req["rollbacks"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if name in chans[channelid]["branches"].keys():
                        if rollbacks < len(chans[channelid]["branches"][name]) - 1:
                            commit = chans[channelid]["branches"][name][rollbacks]["commit"]
                            pack(chans, auths)
                            return {"message": commit}
    return {"status": False}


@app.route("/branches/pull")
def pull():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    # branch = req["branch"]
    name = req["branch"]
    rollbacks = req["rollbacks"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if name in chans[channelid]["branches"].keys():
                        if rollbacks < len(chans[channelid]["branches"][name]) - 1:
                            commit = chans[channelid]["branches"][name][rollbacks]["commit"]
                            data = chans[channelid]["branches"][name][rollbacks]["data"]
                            pack(chans, auths)
                            return {"message": commit, "data": data}
    return {"status": False}


@app.route("/branches/push", methods = ['PUT'])
def push():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    branch = req["branch"]
    # name = req["name"]
    data = req["data"]
    commit = req["commit"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if branch in chans[channelid]["branches"].keys():
                        # {"main":[{"data":"ubudfuwoeub", "commit":"Eat feef"}]}
                        # commit=chans[channelid]["branches"][name][rollbacks]["commit"]
                        # data=chans[channelid]["branches"][name][rollbacks]["data"]
                        chans[channelid]["branches"][branch].insert(0, {"data": data, "commit": commit})
                        pack(chans, auths)
                        return {"status": True}
    return {"status": False}


@app.route("/branches/rollback", methods = ['POST'])
def rollbackf():
    chans, auths = unpack()
    req = request.get_json()
    user, passw = req["auth"]
    channelid = req["channelid"]
    branch = req["branch"]
    amount = req["rollback"]
    if user in auths.keys():
        if auths[user]["pass"] == passw:
            if user in chans[channelid]["shares"]:
                if channelid in chans.keys():
                    if branch in chans[channelid]["branches"].keys():
                        if amount < len(chans[channelid]["branches"][branch]) - 1:
                            for i in range(amount):
                                del chans[channelid]["branches"][branch][0]
                                pack(chans, auths)
                                return {"status": True}
    return {"status": False}

@app.route("/")
def home():
    return "StormShare is still in development. If you want the client, you can't have it. It does not exist yet.<br>Server status: Working(Obviously)"

@app.route("/auth")
def authee():
    return "There is not client and chrome can't pass json to apis. This will not work. Go away."

@app.route("/channels")
def ccccccch():
    return "There is not client and chrome can't pass json to apis. This will not work. Go away."

@app.route("/branches")
def dsss9():
    return "There is not client and chrome can't pass json to apis. This will not work. Go away."

unpack()