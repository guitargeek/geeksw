import uproot

f = uproot.open("./datasets/WWZ/nano_1.root")

print(f.keys())
