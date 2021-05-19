import cv2, re, os, math, pytesseract
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

try:
    from PIL import Image
except ImportError:
    import Image
    
height = 602
width = 295

def crop_and_rotates_image(image, image_mono, file_name):
     (alt, lar) = image_mono.shape[:2]
     _ , imgT = cv2.threshold(image_mono, 200, 255, cv2.THRESH_BINARY)

     p1=0
     xi=lar

     # variavel que valida se a inclinação é positiva ou negativa
     inc=0
     
     for y in range (0,alt,1):
          for x in range (0,lar,1):
               cor = imgT[y,x] 
               if cor!=255 and(p1==0): 
                    ponto1=(x,y)
                    xi=x
                    p1=1
                    if x>(lar/2):
                         inc=1 
                              
               if (p1==1) and (inc==1) and (cor!=255) and (x<xi):
                    ponto2=(x,y)
                    xi=x
                    
               if (p1==1) and (inc==0) and (cor!=255) and (x>xi):
                    ponto2=(x,y)
                    xi=x

     angulo = math.atan2 (ponto1[1]-ponto2[1],ponto1[0]-ponto2[0])

     if inc==1:
          angulo = math.degrees(angulo)

     if inc==0:
          angulo = math.degrees(angulo)+180
          aux=ponto1
          ponto1=ponto2
          ponto2=aux

     # gira img mono
     M = cv2.getRotationMatrix2D(ponto1, angulo, 1.0) 

     # gira imagem original
     original_rotacionada = cv2.warpAffine(image, M, (lar, alt))

     pontoinicial=ponto1

     xi=pontoinicial[0]-height
     xf=pontoinicial[0]
     yi=pontoinicial[1]
     yf=pontoinicial[1]+width

     recorte = original_rotacionada[yi:yf,xi:xf]

     cv2.imwrite(file_name.replace(".", "_cropped."), recorte)

     return recorte

def read_plate_title(cropped_image):
     imagem = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
     thresh = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
     custom_config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNPQRSTUVWXYZ-1234567890 --psm 1'
     texto=(pytesseract.image_to_string(thresh, config=custom_config))
     texto=re.sub(r'[-|\s“"—— \n_]', '', texto)
     return texto
    
def list_files_from_dir(test_path):
     return os.listdir(test_path), os.listdir('gabarito')

def validate_plates(path):
     test_files, template_files = list_files_from_dir(path)

     dict_template_images = {}
     
     for template_path in template_files:
          template_code = template_path.split(' ')[1].replace('.jpg','')
          dict_template_images[template_code] = cv2.imread(f'gabarito/{template_path}')
      
     for file in test_files:
          print("-" * 100)

          complete_path_file = f'{path}/{file}'
          image = cv2.imread(complete_path_file)
          image_mono = cv2.imread(complete_path_file, 0)

          print(f'Arquivo => {complete_path_file}')

          cropped_image = crop_and_rotates_image(image, image_mono, file)
          plate_code = read_plate_title(cropped_image)

          print(f'Gabarito => {plate_code}')

          template = dict_template_images[plate_code]

          try:
               difference = cv2.absdiff(template, cropped_image)
               subtract = cv2.subtract(template, cropped_image)
               ret, difference = cv2.threshold(difference, 127, 255, cv2.THRESH_BINARY)
          except:
               print("Placa => Recusada - As placas tem tamanhos diferentes")
               continue

          b, g, r = cv2.split(difference)

          for y in range (0,template.shape[0],1):
               for x in range (0,template.shape[1],1):
                    if b[y,x] != 0 or g[y,x] != 0 or r[y,x] != 0:
                         cropped_image [y,x]=(0,0,255)

          if cv2.countNonZero(b) < 5000 and cv2.countNonZero(g) < 5000 and cv2.countNonZero(r) < 5000:
               print("Placa => Aceita")

          elif cv2.countNonZero(b) >= 5000 or cv2.countNonZero(g) >= 5000 or cv2.countNonZero(r) >= 5000:
               print("Placa => Recusada - As imagens são diferentes")


if __name__ == '__main__':

     # placas_com_erros
     validate_plates('FotosPlacas')

     # placas_sem_erros
     validate_plates('FotosPlacasComErro')
