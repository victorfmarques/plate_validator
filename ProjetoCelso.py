import cv2, re
import numpy as np
import math
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

try:
    from PIL import Image
except ImportError:
    import Image

placateste = "FotosPlacas\Slide7.jpg"
#placateste = "FotosPlacasComErro\Slide11.jpg"

teste = cv2.imread(placateste)
img = cv2.imread(placateste,0) #monocromática = binária
(alt, lar) = img.shape[:2] #captura altura e largura
ret, imgT = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)



############ INCLINAÇÃO E CORTE #############
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

#cv2.imshow("Imagem original com marcações", teste)
                       
angulo = math.atan2 (ponto1[1]-ponto2[1],ponto1[0]-ponto2[0])
if inc==1:
    angulo = math.degrees(angulo)
if inc==0:
    angulo = math.degrees(angulo)+180
    aux=ponto1
    ponto1=ponto2
    ponto2=aux

############ girando a imagem monocromatica          
M = cv2.getRotationMatrix2D(ponto1, angulo, 1.0) 
img_rotacionada = cv2.warpAffine(imgT, M, (lar, alt))
#cv2.imshow("Imagem rotacionada", img_rotacionada)

############ girando a imagem original  
original_rotacionada = cv2.warpAffine(teste, M, (lar, alt))
#cv2.imshow("Original rotacionada", original_rotacionada)

######### cortando a imagem original
pontoinicial=ponto1
larguraPlaca = 602
alturaPlaca = 295

xi=pontoinicial[0]-larguraPlaca
xf=pontoinicial[0]
yi=pontoinicial[1]
yf=pontoinicial[1]+alturaPlaca

recorte = original_rotacionada[yi:yf,xi:xf]
#cv2.imshow("cortada", recorte)
cv2.imwrite("Recorte.jpg", recorte) #salva no disco




###################### OCR ###########################

imagem = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
#cv2.imshow("asd", imagem)
thresh = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#cv2.imshow("Teste", thresh)

custom_config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNPQRSTUVWXYZ-1234567890 --psm 1'
texto=(pytesseract.image_to_string(thresh, config=custom_config))
texto=re.sub(r'[-|\s“"—— \n_]', '', texto)
    
print('Reconhecido: ', texto)



########### VERIFICAR MODELO DE GABARITO ##############


if texto == "AB01": gabarito = cv2.imread("gabarito/Gabarito AB01.jpg")
elif texto == "AB02": gabarito = cv2.imread("gabarito/Gabarito AB02.jpg")
elif texto == "AC01": gabarito = cv2.imread("gabarito/Gabarito AC01.jpg")
elif texto == "AC02": gabarito = cv2.imread("gabarito/Gabarito AC02.jpg")



############# COMPARAR IMAGENS ##############


def confereab(qx, qy, rx1, rx2, rx3, ry):
    (b, g, r) = recorte[qy,qx]
    mark = 0
    
    if b == 0 and g == 0 and r == 255:
        print("Falta o quadrado!")

    (b, g, r) = recorte[ry,rx1]
    if b == 0 and g == 0 and r == 255:
        mark += 1
    (b, g, r) = recorte[ry,rx2]
    if b == 0 and g == 0 and r == 255:
        mark += 1
    (b, g, r) = recorte[ry,rx3]
    if b == 0 and g == 0 and r == 255:
        mark += 1

    if mark == 3:
        print ("Falta o retângulo!")
    elif mark > 0:
        print ("Retângulo incompleto!")

def confereac(qx, qy, ry1, ry2, ry3, rx):
    (b, g, r) = recorte[qy,qx]
    mark = 0

    if b == 0 and g == 0 and r == 255:
        print("Falta o quadrado!")

    (b, g, r) = recorte[ry1,rx]
    if b == 0 and g == 0 and r == 255:
        mark += 1
    (b, g, r) = recorte[ry2,rx]
    if b == 0 and g == 0 and r == 255:
        mark += 1
    (b, g, r) = recorte[ry3,rx]
    if b == 0 and g == 0 and r == 255:
        mark += 1

    if mark == 3:
        print ("Falta o retângulo!")
    elif mark > 0:
        print ("Retângulo incompleto!")

    

difference = cv2.absdiff(gabarito, recorte)
subtract = cv2.subtract(gabarito, recorte)

ret, difference = cv2.threshold(difference, 127, 255, cv2.THRESH_BINARY)


cv2.imshow("Teste", difference)

b, g, r = cv2.split(difference)

for y in range (0,gabarito.shape[0],1):
    for x in range (0,gabarito.shape[1],1):
        if b[y,x] != 0 or g[y,x] != 0 or r[y,x] != 0:
            recorte [y,x]=(0,0,255)

if cv2.countNonZero(b) < 5000 and cv2.countNonZero(g) < 5000 and cv2.countNonZero(r) < 5000:
    print("Placa aceita")


elif cv2.countNonZero(b) >= 5000 or cv2.countNonZero(g) >= 5000 or cv2.countNonZero(r) >= 5000:
    print("Placa recusada")
    if texto == "AB01":
        qx = 86
        qy = 83
        ry = 220
        rx1 = 285
        rx2 = 400
        rx3 = 520
        confereab(qx, qy, rx1, rx2, rx3, ry)

    elif texto == "AB02":
        qx = 90
        qy = 150
        ry = 150
        rx1 = 285
        rx2 = 400
        rx3 = 520
        confereab(qx, qy, rx1, rx2, rx3, ry)
        
    elif texto == "AC01":
        qx = 105
        qy = 220
        rx = 430
        ry1 = 60
        ry2 = 150
        ry3 = 240
        confereac(qx, qy, ry1, ry2, ry3, rx)
        
    elif texto == "AC02":
        qx = 285
        qy = 155
        rx = 432
        ry1 = 70
        ry2 = 150
        ry3 = 240
        confereac(qx, qy, ry1, ry2, ry3, rx)
        

cv2.imshow("Original", gabarito)
cv2.imshow("recorte", recorte)


# Para a analise de se está errado ou fora de posição
# comparar se está vermelho no local correto do objeto
# e para objetos fora de posição, analisar se há outro objeto
# de mesmo tamanho em outra posição da placa.



############# VERIFICAR OBJETO FORA DE LUGAR ##############

ret, subtract = cv2.threshold(subtract, 127, 255, cv2.THRESH_BINARY)
cv2.imshow("Elemento", subtract)

b, g, r = cv2.split(subtract)

if cv2.countNonZero(g) >= 18000 and cv2.countNonZero(r) >= 18000:
    print("O retangulo está fora da posição correta!")
elif cv2.countNonZero(g) >= 8000 or cv2.countNonZero(r) >= 8000:
    print("O quadrado está fora da posição correta!")


print (cv2.countNonZero(b))
print (cv2.countNonZero(g))
print (cv2.countNonZero(r))
cv2.waitKey(0)