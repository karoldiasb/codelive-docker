import fileinput
import sys
saida = 0
for line in fileinput.input():
saida += int(line[0])
print(saida)