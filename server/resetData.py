import pickle, os
#for i in range(20):
    #input(f"Press enter {20-i} more times to reset data.")
os.remove("auths.dat")
os.remove("chans.dat")
chans={}
with open("chans.dat", mode="wb") as dde:
    pickle.dump(chans, dde)
auths = {}
with open("auths.dat", mode="wb") as dde:
    pickle.dump(auths, dde)
print("Data reset.")