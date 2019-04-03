import numpy as np
import random
import time
# import cv2
from direct.showbase.ShowBase import ShowBase
from panda3d.core import FrameBufferProperties, WindowProperties
from panda3d.core import GraphicsPipe, GraphicsOutput
# from panda3d.core import Texture

from panda3d.core import PandaNode
from panda3d.core import Vec3
from panda3d.core import Spotlight
from panda3d.core import GraphicsPipeSelection
from panda3d.core import Camera
from panda3d.core import NodePath
from panda3d.core import loadPrcFileData
import  memory_profiler

loadPrcFileData('', 'window-type none')

class MyApp(ShowBase):
    def __init__(self, screen_size=84):
        ShowBase.__init__(self)
        self.render.setShaderAuto()

        # Offscreen Buffer
        winprops = WindowProperties.size(screen_size, screen_size)
        fbprops = FrameBufferProperties()
        self.pipe = GraphicsPipeSelection.get_global_ptr().make_module_pipe('pandagl')
        self.imageBuffer = self.graphicsEngine.makeOutput(
            self.pipe,
            "image buffer",
            1,
            fbprops,
            winprops,
            GraphicsPipe.BFRefuseWindow)

        # Camera
        self.camera = Camera('cam')
        self.cam = NodePath(self.camera)
        self.cam.reparentTo(self.render)
        self.cam.setPos(0, 0, 7)
        self.cam.lookAt(0, 0, 0)

        #Display Region
        self.dr = self.imageBuffer.makeDisplayRegion()
        self.dr.setCamera(self.cam)

        # Spotlight with shadows
        self.light = Spotlight('light')
        self.lightNP = self.render.attachNewNode(self.light)
        self.lightNP.setPos(0, 10, 10)
        self.lightNP.lookAt(0, 0, 0)
        self.lightNP.node().setShadowCaster(True, 1024, 1024)
        self.render.setLight(self.lightNP)

        # Block
        node = PandaNode('Block')
        block_np = self.render.attachNewNode(node)
        model = loader.loadModel('box.egg')
        model.reparentTo(block_np)

        self.start_time = time.time()


    def get_camera_image(self, requested_format=None):
        tex = self.dr.getScreenshot()
        data = self.dr.getScreenshot().getRamImage()
        image = np.frombuffer(data, np.uint8)
        return image


    def rotate_light(self):
        radius = 10
        step = 0.1
        t = time.time() - self.start_time
        angleDegrees = t * step
        angleRadians = angleDegrees * (np.pi / 180.0)
        self.lightNP.setPos(radius * np.sin(angleRadians), -radius * np.cos(angleRadians), 3)
        self.lightNP.lookAt(0, 0, 0)


    def step(self):
        self.rotate_light()
        self.graphicsEngine.renderFrame()
        image = self.get_camera_image()
        return image


def main():
    app = MyApp(screen_size=84*1)
    step_num = 0
    last_mem = memory_profiler.memory_usage()[0]
    app.start_time = time.time()
    while True:
        step_num += 1
        image = app.step()
        # cv2.imshow('state', image)
        # key = cv2.waitKey(1) & 0xFF
        # if key == 27 or key == ord('q'):
        #     print("Pressed ESC or q, exiting")
        #     exit()

        # Memory Usage
        if step_num % 1000 == 0:
            now_mem = memory_profiler.memory_usage()[0]
            if step_num != 1000:
                print('Memory per 1k steps:', now_mem-last_mem, 'MB')
            last_mem = now_mem

if __name__ == '__main__':
    main()
