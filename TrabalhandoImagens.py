import cv2
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
import math

cv2.destroyAllWindows()
arquivo='original1.jpg'
original = cv2.imread(arquivo) #colorida
img = cv2.imread(arquivo,0) #monocromática = binária
(alt, lar) = img.shape[:2] #captura altura e largura
ret, imgT = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)#230

############ descobrindo a inclinação da imagem
p1=0
p2=0
xi=lar
inc=0

for y in range (0,alt,1):
    for x in range (0,lar,1):
        cor = imgT[y,x] 
        if cor!=255 and(p1==0): 
            ponto1=(x,y)
            xi=x
            p1=1
            if x>(lar/2):
                inc=1 # para saber se a inclinação é positiva ou negativa
                        
        if (p1==1) and (inc==1) and (cor!=255) and (x<xi):
            ponto2=(x,y)
            xi=x
            
        if (p1==1) and (inc==0) and (cor!=255) and (x>xi):
            ponto2=(x,y)
            xi=x

cv2.circle(original, (ponto1), 5, (0, 255, 0), -1)
cv2.circle(original, (ponto2), 5, (0, 255, 0), -1)

cv2.imshow("Imagem original com marcações", original)
                       
angulo = math.atan2 (ponto1[1]-ponto2[1],ponto1[0]-ponto2[0])
if inc==1:
    angulo = math.degrees(angulo)
if inc==0:
    angulo = math.degrees(angulo)+180
    aux=ponto1
    ponto1=ponto2
    ponto2=aux
    
print ('Inclinacao = ', angulo)

############ girando a imagem monocromatica          
M = cv2.getRotationMatrix2D(ponto1, angulo, 1.0) 
img_rotacionada = cv2.warpAffine(imgT, M, (lar, alt))
cv2.imshow("Imagem rotacionada", img_rotacionada)

############ girando a imagem original  
original_rotacionada = cv2.warpAffine(original, M, (lar, alt))
cv2.imshow("Original rotacionada", original_rotacionada)

######### cortando a imagem original
pontoinicial=ponto1
larguraPlaca = 609
alturaPlaca = 264

xi=pontoinicial[0]-larguraPlaca
xf=pontoinicial[0]
yi=pontoinicial[1]
yf=pontoinicial[1]+alturaPlaca

recorte = original_rotacionada[yi:yf,xi:xf]
cv2.imshow("Recorte da imagem", recorte)
cv2.imwrite("Recorte.jpg", recorte) #salva no disco

cv2.waitKey(0) 
