
import re


text = 'sadasdasdsad asd sa sa sa as as ads-48,27EUR\r\nValor a Receber\r\ndsadsadasdsadasdasdasdas'
regex = r'^[^0-9]*(-?\d+[.,]?\d*)EUR\r\nValor a Receber\r\n'

x = re.search(regex, text)
pos_ini = x.regs[1][0]
pos_fim = x.regs[1][1]
print(text[pos_ini:pos_fim])
