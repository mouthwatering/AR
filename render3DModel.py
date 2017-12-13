from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame, pygame.image
from pygame.locals import *
import numpy
import pickle

width, height = 1200,747

def set_projection_from_camera(K):
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()

  fx = float(K[0, 0])
  fy = float(K[1, 1])
  fovy = 2 * numpy.arctan(0.5 * height / fy) * 180 / numpy.pi
  aspect = (width * fy) / (height * fx)
  near, far = 0.1, 100
  gluPerspective(fovy, aspect, near, far)
  glViewport(0, 0, width, height)


def set_modelview_from_camera(Rt):
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

  # Rotate 90 deg around x, so that z is up.
  Rx = numpy.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
  # Remove noise from rotation, make sure it's a pure rotation.
  R = Rt[:, :3]
  U, S, V = numpy.linalg.svd(R)
  R = numpy.dot(U, V)
  R[0, :] = -R[0, :]  # Change sign of x axis.

  print(S)
  t = Rt[:, 3]

  M = numpy.eye(4)
  M[:3, :3] = numpy.dot(R, Rx)
  M[:3, 3] = t

  m = M.T.flatten()
  glLoadMatrixf(m)

def draw_background(imname):

  width, height = bg_image.get_size()
  bg_data = pygame.image.tostring(bg_image, "RGBX", 1)

  glEnable(GL_TEXTURE_2D)
  tex = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, tex)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
               GL_RGBA, GL_UNSIGNED_BYTE, bg_data)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

  glBegin(GL_QUADS)
  glTexCoord2f(0, 0); glVertex3f(-1, -1, -1)
  glTexCoord2f(1, 0); glVertex3f( 1, -1, -1)
  glTexCoord2f(1, 1); glVertex3f( 1,  1, -1)
  glTexCoord2f(0, 1); glVertex3f(-1,  1, -1)
  glEnd()

  glDeleteTextures(tex)


def load_and_draw_model2(foldername, filename):
  viewport = (1200, 747)
  srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

  import objloader
  # LOAD OBJECT AFTER PYGAME INIT
  obj = objloader.OBJ(foldername,filename, swapyz=True)

  clock = pygame.time.Clock()

  rx, ry = (0, 0)
  tx, ty = (0, 0)
  zpos = 5
  rotate = move = False
  onlyone = True
  while onlyone:
    clock.tick(30)
    for e in pygame.event.get():
      if e.type == QUIT:
        sys.exit()
      elif e.type == KEYDOWN and e.key == K_ESCAPE:
        sys.exit()
      elif e.type == MOUSEBUTTONDOWN:
        if e.button == 4:
          zpos = max(1, zpos - 1)
        elif e.button == 5:
          zpos += 1
        elif e.button == 1:
          rotate = True
        elif e.button == 3:
          move = True
      elif e.type == MOUSEBUTTONUP:
        if e.button == 1:
          rotate = False
        elif e.button == 3:
          move = False
      elif e.type == MOUSEMOTION:
        i, j = e.rel
        if rotate:
          rx += i
          ry += j
        if move:
          tx += i
          ty -= j

    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE,GL_ZERO )
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_background('background-1.png')
    glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)  # most obj files expect to be smooth-shaded

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width / float(height), 1, 100.0)

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # RENDER OBJECT
  #  glTranslate(tx / 20., ty / 20., - zpos)
    glTranslate(-0.4, -1, - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glScale(0.03, 0.03, 0.03)
    glCallList(obj.gl_list)

    pygame.display.flip()

def setup():
  pygame.init()
  pygame.display.set_mode((width, height), OPENGL | DOUBLEBUF)
  pygame.display.set_caption('OpenGL AR demo')


with open('data/ar_camera.pkl', 'r') as f:
  K = pickle.load(f)
  Rt = pickle.load(f)


setup()

bg_image = pygame.image.load('background-1.png').convert()

set_projection_from_camera(K)
set_modelview_from_camera(Rt)

load_and_draw_model2('Corona','Corona.obj')

while True:
  event = pygame.event.poll()
  if event.type in (QUIT, KEYDOWN):
    break
  pygame.display.flip()
