import time
import pyautogui
import logging
from cv2 import cv2
from os import listdir
from random import randint
from random import random
import mss
import numpy as np

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

pyautogui.PAUSE = 5

def addRandomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """

    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)
    
def printScreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        
        return sct_img[:,:,:3]
    
def positions(target, threshold=0.7,img = None):
    if img is None:
        img = printScreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles
    
def clickBtn(img, timeout=3, threshold = 0.7):
    """Search for img in the screen, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches)==0):
            has_timed_out = time.time()-start > timeout
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

    return False    


def click_on_image(image_name,process,delay=10):
    cords = pyautogui.locateCenterOnScreen(image_name,confidence=0.9)
    if(cords):
        logging.info(f'{process} detectado.')
        pyautogui.click(cords)
        time.sleep(delay)
        return True
    else:
        logging.info(f'{process} não detectado.')
        return False


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./assets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'assets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def login():
    logging.info('Iniciando login...')

    if  clickBtn(images['luna-login-2'],timeout=10,threshold=0.9):
        logging.info('Login realizado com sucesso.')
        if(click_on_image('assets/metamask-sign.png','Metamask',10)): 
            logging.info('Metamask detectado.')
            return True
        else:
            logging.info('Metamask não detectado.')
            return False  
    else:
        logging.info('Falha ao realizar o login')       
        return False
    

def hunt_boss():
    
    if(click_on_image('assets/hunt-boss.png','Hunt Boss',10)):
        logging.info('Hunt Boss realizado com sucesso.')
        if(click_on_image('assets/not-full.png','Boss não full energy',5)):
            send_to_fight()
        else:
            logging.info('Hunt Boss está full.')
        return True    
    else:
        logging.info('Hunt Boss não detectado.')
        return False


def send_to_fight():
    
      clickCounter = 0
      fightCounter = 0
      while (clickCounter <= 3):
        cordsFullEnergy = pyautogui.locateCenterOnScreen('assets/full-hero.png',confidence=0.9)
        if(cordsFullEnergy):
          logging.info('Enviando para lutar...')
          pyautogui.click(cordsFullEnergy)
          if(clickCounter <= 3):
               clickCounter += 1
        logging.info(clickCounter <= 3)
        logging.info(f'Cliando no Hero {clickCounter}.')
      else:
        while (fightCounter <= 3):  
            logging.info('Começando a luta.')
            cordsFight = pyautogui.locateCenterOnScreen('assets/play.png',confidence=0.9)
            fightCounter +=1
            logging.info(f'Lutando {fightCounter} vez.')
            time.sleep(5)
            pyautogui.click(cordsFight)
            clickCounter = 0        
            time.sleep(25)
            cordsWinFight = pyautogui.locateCenterOnScreen('assets/next-win.png',confidence=0.9)
            if(cordsWinFight):
                logging.info('Vitória detectada.')
                pyautogui.click(cordsWinFight)
                time.sleep(10)
                cordsContinue = pyautogui.locateCenterOnScreen('assets/next.png',confidence=0.9)
                if(cordsContinue):
                    logging.info('Continuando...')
                    pyautogui.click(cordsContinue)
                    time.sleep(10)
            else:
                logging.info('Entrei no else') 
                cordsContinue = pyautogui.locateCenterOnScreen('assets/next.png',confidence=0.9)
                if(cordsContinue):
                    logging.info('Continuando...')
                    pyautogui.click(cordsContinue)
                    time.sleep(10)
        else:
            logging.info('Fim do loop.')
def main():
    global images
    images = load_images()

    try:
        logging.info('Iniciando bot...')
        loginLuna = login()
        print(loginLuna)
        if(loginLuna):
            logging.info('Iniciando o hunt boss...')
            time.sleep(10)
            hunt_boss()
        
            send_to_fight()
    except Exception as e:
        logging.error(f'ERROR: {e} - Erro ao executar o bot.')
        #else:
        #   logging.info('Login não realizado.')

main()    