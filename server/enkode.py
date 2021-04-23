def enkode(string):
    lenEnc=len(string)
    newStorng=""
    for ind,i in enumerate(string):
        newStorng+=chr((ord(i)+lenEnc*ind)%256)
        #print(lenEnc*ind)
    encoded=newStorng[::-1]
    return encoded

original="Hello! My name is alex. My brother's name is Dennis."

encoded=enkode(original)

def dekode(string):
    lenDec = len(string)
    decstring=string[::-1]
    decoded=""
    for ind,i in enumerate(decstring):
        decoded+=chr((ord(i)-(lenDec*ind))%256)
    return decoded

decoded=dekode(encoded)
print(original)
print(encoded)
print(decoded)