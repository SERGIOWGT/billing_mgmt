import re


txt = "xzxzxZFatura\r\nfevereiro 2023ZXzzxzXZ"
x = re.search('Fatura\r\n\w+ [0-9]{4}', txt)
print(txt[6:28])
