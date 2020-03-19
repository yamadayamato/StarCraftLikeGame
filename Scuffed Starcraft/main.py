import pygame                   #init(), display()
from pygame.locals import *     #QUIT, USEREVENT, ect.
import pygame.mixer
import os                       #getcwd(), os.environ
import sys                      #version()
import math
import numpy as np

import Entity
import input
import mathfuncs
import Map
import Worker
import playerinfo
import Mineral
import Overlay

class App():
    def __init__(self):
        self._running = True
        self._display_surf = None       #UI Surface/Foreground/Display Window (800x600)
        self._display_surfrender = None #Background/Map
        self._image_surf = None         #??
        self._cwdpath = None            #Get working directory to retrieve images 

    def on_init(self):
        #(from: on_execute)
        #Puts pygame window in the middle
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        #Check that Mixer was initiated. on_execute will fail/stop the program otherwise.
        if self.initpygame() is False:
            return False

        #Initialize Game Window
        # (Not Used Yet!) Video Display Object: If called before pygame.display.set_mode() can provide user's screen resolution
        self._infoObject = pygame.display.Info()
        # Map Image in Background (Needs to be rendered)
        self._display_surfrender = pygame.Surface((1500,1500))
        # Window Size
        self._display_surf = pygame.display.set_mode((800,600), pygame.RESIZABLE)
        # CWD path for images
        self._cwdpath = os.getcwd()
        pygame.display.set_caption("Scuffed StarCraft")
        pygame.display.set_icon(pygame.image.load(os.path.join(self._cwdpath,"Images","sc2.png")))
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        #Initialize FPS value (see .handlefps())
        self._lasttime = 0

        self._input = input.input()
        self._playerinfo = playerinfo.playerinfo()

        #Initialize Map Dimensions and Camera Set-Up
        self.map = Map.Map()

        #Initialize Overlay (UI)
        self.overlay = Overlay.Overlay()

        #Initialize Cursor/Map/Sounds and other general media
        self.load_media()

        #Initialize Troops and smaller entities
        self.load_entities()

        #Initialize Map resources
        self.load_resources()


    def initpygame(self):
        #(from: on_execute-> on_init)
        #Check that Mixer was initiated. on_execute will fail/stop the program otherwise.
        pygame.init()
        pygame.mixer.init()
        if pygame.mixer.get_init() is None:
            print("Error initializing mixer!\n")
            return False

    def load_resources(self):
        #minerals
        self.minerallist = []
        mineral1 = Mineral.Mineral(450,450,self._mineralimg)
        mineral2 = Mineral.Mineral(500,400,self._mineralimg)
        mineral3 = Mineral.Mineral(600,350,self._mineralimg)
        self.minerallist.append(mineral1)
        self.minerallist.append(mineral2)
        self.minerallist.append(mineral3)

    def load_entities(self):
        marinesurf = pygame.image.load(os.path.join(self._cwdpath,"Images","marauder.png")).convert()
        scvsurf = pygame.image.load(os.path.join(self._cwdpath,"Images","scv2.png")).convert_alpha()
        marinerect = pygame.Rect(0,0,85,85)
        entity1 = Worker.Worker(25,scvsurf,marinerect)
        marinerect = pygame.Rect(100,50,85,85)
        entity2 = Worker.Worker(25,scvsurf,marinerect)
        self._entitylist = []
        self._entitylist.append(entity1)
        self._entitylist.append(entity2)
        self.line = [(100,100),(200,200)]
        self.circle = (200,100,20)
        self.pumpcircle = (400,250,80)

    def load_media(self):
        #(from: on_execute-> on_init)
        #Load general sounds and images
        self._image_surf = pygame.image.load(os.path.join(self._cwdpath,"Images","lilpump.jpg")).convert()
        self._mineralimg = pygame.image.load(os.path.join(self._cwdpath,"Images","mineralt.png")).convert_alpha()

        #Background Map (stored in map object)
        self.map._mapimage = pygame.image.load(os.path.join(self._cwdpath,"Images","bigmap3.jpg")).convert()

        #Directional Green Cursor
        self._mouseimg1 = pygame.image.load(os.path.join(self._cwdpath,"Images","mouse1t.png")).convert_alpha()
        self._mouseimg2 = pygame.image.load(os.path.join(self._cwdpath,"Images","mouse2t.png")).convert_alpha()
        self._mouseimg3 = pygame.image.load(os.path.join(self._cwdpath,"Images","mouse3t.png")).convert_alpha()
        self._mouseimg4 = pygame.image.load(os.path.join(self._cwdpath,"Images","mouse4t.png")).convert_alpha()
        self._mouseimg5 = pygame.image.load(os.path.join(self._cwdpath,"Images","mouse5t.png")).convert_alpha()
        self._mouseimgoffset = np.array([10,10])
        self._mouseimglist = [self._mouseimg1,self._mouseimg2,self._mouseimg3,self._mouseimg4,self._mouseimg5]
        self._mouseimgcurrent = self._mouseimg1
        self.sound_esketit = pygame.mixer.Sound(os.path.join(self._cwdpath,"Sounds","esketit.wav"))

        #Overlay
        self.overlay.overlayimage = pygame.image.load(os.path.join(self._cwdpath,"Images/Overlay","CleanBottomOverlay.png")).convert_alpha()

    def on_update(self):
        #update map and mouse information
        mouseinfo = self.map.handleinput(self._input, self._display_surf,self._mouseimgcurrent, self._mouseimglist)
        self._mouseimgcurrent = self._mouseimglist[mouseinfo[0]]
        self._mouseimgoffset[0] = mouseinfo[1]
        self._mouseimgoffset[1] = mouseinfo[2]

        self._playerinfo.update(self._input, self._entitylist,self.map,self._display_surf)

        for units in self._entitylist:
            units.update(self._input,self.minerallist, self.map,self._display_surf)

        #for units in self._playerinfo._selectedlist:
            #units.handleinput(self)

        answer = mathfuncs.mathfuncs.circlesegcollision(self._entitylist[0].radius,self._entitylist[0].circlecenter[0],self._entitylist[0].circlecenter[1],
        self.line[0][0],self.line[0][1],self.line[1][0],self.line[1][1])
        answer2 = mathfuncs.mathfuncs.circlecirclecollision((self._entitylist[0].circlecenter[0],self._entitylist[0].circlecenter[1],
         self._entitylist[0].radius), self.circle)
        #print("Line collision: %d Circle collision: %d" % (answer, answer2))
        if mathfuncs.mathfuncs.circlecirclecollision((self._entitylist[0].circlecenter[0],self._entitylist[0].circlecenter[1], self._entitylist[0].radius), self.pumpcircle):
            self.sound_esketit.set_volume(.05)
            self.sound_esketit.play();

        #if not pygame.mixer.music.get_busy():
        #    pygame.mixer.music.load(os.path.join(self._cwdpath,"Sounds","100 on my wrist.wav"))
        #    pygame.mixer.music.set_volume(0.5)
        #    pygame.mixer.music.play()
            #self.sound_esketit.set_volume(.05)
            #self.sound_esketit.play();

    def on_render(self):
        #(from: on_execute)

        #map (set up camera dimensions on map to avoid going out of bounds)
        self.map.render(self._display_surfrender)

        #units
        for x in self._entitylist:
            x.render(self)

        #minerals
        for x in self.minerallist:
            x.render(self)

        #map cont. - render map to fit window size
        # MUST BE AFTER rendering units and minerals or they will not appear!
        resized_screen = pygame.transform.scale(self._display_surfrender, (self._display_surf.get_width(),self._display_surf.get_height()))
        self._display_surf.blit(resized_screen, (0, 0))

        #UI - ORDER MATTERS!
        #bottom Overlay
        self.overlay.render(self._display_surf)

        self.overlay.renderGameClock(self._display_surf)
     
        #mini map
        self.map.renderminimap(self._display_surf)
        #green box
        self._playerinfo.render(self._display_surf)

        #cursor
        mousesize = 44
        self.drawimagerectgui(pygame.Rect(self._input.mouseposition[0] - int(mousesize/2) + self._mouseimgoffset[0],
          self._input.mouseposition[1] - int(mousesize/2) + self._mouseimgoffset[1],mousesize,mousesize),self._mouseimgcurrent)

        pygame.display.update()

    def drawimagerect(self, rect, image): #renders an image on a rect while preserving original image size
        newimage = pygame.transform.scale(image,(rect.w,rect.h))
        self._display_surfrender.blit(newimage,(rect.x,rect.y))

    def drawimagerectgui(self, rect, image):
        newimage = pygame.transform.scale(image,(rect.w,rect.h))
        self._display_surf.blit(newimage,(rect.x,rect.y))

    def on_exit(self):
        self._running = False

    def on_cleanup(self):
        #(from: on_execute)
        #Quit Mixer and PyGames
        pygame.quit()
        pygame.mixer.quit()

    def on_execute(self):
        #Initialize the window, camera, media and other entities. Return false if
        #there is an error on initiating Mixer.
        if self.on_init() == False:
            self._running = False

        #Main Game Running
        while( self._running ):
            self._input.reset()
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.on_render()
            self.handlefps()

        #Quit Mixer and PyGames
        self.on_cleanup()

    def handlefps(self):
        #(from: on_execute)
        #Display user's FPS in upper right-hand corner of the screen
        frametime = pygame.time.get_ticks() - self._lasttime
        if frametime != 0:
            fps = 1000 / frametime #1000 miliseconds = 1 second, so
            pygame.display.set_caption("Scuffed StarCraft fps: %f" % fps)
            if frametime < 17:
                pygame.time.delay(17 - frametime)
        self._lasttime = pygame.time.get_ticks()

    def on_event(self, event): 
        #(from: on_execute)

        #INPUT HANDLING FUNCTION
        #Change _running to false to get out of infinite loop and exit program
        if event.type == QUIT:
            self.on_exit()

        elif event.type >= USEREVENT:
            pass

        elif event.type == VIDEOEXPOSE:
            pass

        elif event.type == VIDEORESIZE: # event.size, event.w, event.h
            self._display_surf = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            pass

        elif event.type == KEYUP:
            self._input.keys[event.key] = 0

        elif event.type == KEYDOWN: #event.key (pygame.K_x) event.mod == pygame.KMOD_LSHIFT
            speed = 10
            self._input.keys[event.key] = 1
            if event.key == pygame.K_1:
                pygame.display.set_mode((800, 600),  pygame.RESIZABLE)
            if event.key == pygame.K_2:
                pygame.display.set_mode((1350,750),  pygame.RESIZABLE)
                pygame.display.update()
            if event.key == pygame.K_ESCAPE:
                self.on_exit()

        elif event.type == MOUSEMOTION: #event.buttons, event.pos, event.rel
            self._input.mouseposition = event.pos
            self._input.mousechange = event.rel

        elif event.type == MOUSEBUTTONUP: #event.button, #event.pos
            if event.button == 1:
                self._input.leftclick = False
                self._input.leftclickletgo = True
            elif event.button == 2:
                pass
            elif event.button == 3:
                self._input.right = False

        elif event.type == MOUSEBUTTONDOWN: #event.button, #event.pos
            if event.button == 1: #l
                self._input.leftclick = True
                self._input.leftclickframe = True
                self._input.mouseclickposition = event.pos
            elif event.button == 2: #m
                pass
            elif event.button == 3: #r
                self._input.rightclick = True
                self._input.rightclickframe = True
                self._input.mouseclickposition = event.pos
            elif event.button == 4: #r
                self._input.mousewheel = 1
            elif event.button == 5: #r
                self._input.mousewheel = -1

        elif event.type == ACTIVEEVENT:
            if event.state == 1:
                if event.gain:
                    pass #self.on_mouse_focus()
                else:
                    pass #self.on_mouse_blur()
            elif event.state == 2:
                if event.gain:
                    pass #self.on_input_focus()
                else:
                    pass #self.on_input_blur()
            elif event.state == 4:
                if event.gain:
                    pass #self.on_restore()
                else:
                    pass #self.on_minimize()

if __name__ == "__main__" :
    print(sys.version)
    theApp = App()
    theApp.on_execute()