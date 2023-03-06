import pygame
import math
import random

# import the scene class
from cubeMap import FlattenCubeMap
from scene import Scene

from lightSource import LightSource

from blender import load_obj_file

from BaseModel import DrawModelFromMesh

from shaders import *

from ShadowMapping import *


from skyBox import *

from environmentMapping import *

# determines if a tree is within the parabola (water)
def placeTree(x, y):
    return -0.2*(x-3)**2 < y
    
# generates the tree model if it is not within the water    
def randomTree(self, treeModel):
        x = random.uniform(-15, 15)
        y = random.uniform(-15, 15)
        #if the tree is within the water it is not placed
        if placeTree(x, y) == True:
            return [DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(rotationMatrixY(math.pi), scaleMatrix([0.5, 0.7, 0.5])), translationMatrix([x, -5, y])), mesh=mesh, shader=PhongShader(), name='single_tree1') for mesh in treeModel]

class JungleScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        # light for the scene
        self.light = LightSource(self, position=[9, 9, 5.])

        self.shaders='phong'

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        # load the three different tree models and list to contain them
        single_tree = load_obj_file('models/single_tree.obj')
        double_tree = load_obj_file('models/double_tree.obj')
        triple_tree = load_obj_file('models/triple_tree.obj')
        self.trees=[[]]

        # generate random trees for each of the 3 tree models
        for i in range(20):
            single = randomTree(self, single_tree)
            if single is not None:
                self.trees.append(single)
            double = randomTree(self, double_tree)
            if double is not None:
                self.trees.append(double)
            triple = randomTree(self, triple_tree)
            if triple is not None:
                self.trees.append(triple)


        # generation of the two animal models
        hippo = load_obj_file('models/Hippo.obj')
        self.hippo = DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(translationMatrix([-3, -4, 3.5]), scaleMatrix([0.5, 0.5, 0.5])), rotationMatrixY(math.pi/4)), mesh=hippo[0], shader=PhongShader())

        self.transObjects = [self.hippo]

        tiger = load_obj_file('models/tiger2.obj')[1::]
        self.tiger = [DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(translationMatrix([-0.75, -4.25, 4.5]), scaleMatrix([0.25, 0.25, 0.25])), rotationMatrixY(-math.pi/4)), mesh=mesh, shader=PhongShader(), name='tiger') for mesh in tiger]
        
        aztec = load_obj_file('models/aztec.obj')
        self.aztec = [DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(translationMatrix([2, -4.5, 5]), scaleMatrix([1, 1, 1])), rotationMatrixY(-math.pi/4)), mesh=mesh, shader=PhongShader(), name='tiger') for mesh in aztec]


        # draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)

        self.environment = EnvironmentMappingTexture(width=400, height=400)

        # uses environment mapping
        diamond = load_obj_file('models/diamond.obj')
        self.diamond = DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(translationMatrix([2, -3.25, 5]), scaleMatrix([0.4, 0.4, 0.4])), rotationMatrixY(math.pi/4)), mesh=diamond[0], shader=EnvironmentShader(map=self.environment))


        # ground and water models fro the scene
        ground = load_obj_file('models/ground3.obj')
        self.ground = DrawModelFromMesh(scene=self, M=np.matmul(scaleMatrix([0.75, 1, 0.75]), np.matmul(translationMatrix([0,-3.5,0]), rotationMatrixY(math.pi))), mesh=ground[0], shader=ShadowMappingShader(shadow_map=self.shadows))

        water = load_obj_file('models/water.obj')
        self.water = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-4, 2]), scaleMatrix([2,1,2])), mesh=water[0], shader=ShadowMappingShader(shadow_map=self.shadows))

    

    # draw all of the shadows for the scene
    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.ground.draw()
        self.water.draw()
        self.hippo.draw()
        self.diamond.draw()

        for tree in self.trees:
            for model in tree:
                model.draw()

        for model in self.tiger:
            model.draw()

    # draw all of the reflections for the scene
    def draw_reflections(self):
        self.skybox.draw()

        self.ground.draw()
        self.water.draw()
        self.hippo.draw()
        self.diamond.draw()

        for tree in self.trees:
            for model in tree:
                model.draw()

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # when using a framebuffer, we do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()

        # first, we draw the skybox
        self.skybox.draw()

        # render the shadows
        self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            #self.envbox.draw()
            self.environment.update(self)
            #self.envbox.draw()

            self.environment.update(self)

            # draw the single mesh models
            self.ground.draw()
            self.water.draw()
            self.hippo.draw()
            self.diamond.draw()

            

            glDisable(GL_BLEND)

            self.show_shadow_map.draw()

        # draw all of the trees
        for tree in self.trees:
            for model in tree:
                model.draw()

        # draw the multiple mesh model
        for model in self.tiger:
            model.draw()

        for model in self.aztec:
            model.draw()



        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Key presses to translate and rotate the hippo model

        Translation

        W -> Y pos
        S -> Y neg
        D -> X pos
        A -> X neg
        LSHIFT -> Z pos
        LCTRL -> Z neg


        Rotation (arrow keys)

        UP -> Y pos
        DOWN -> Y neg
        RIGHT -> X pos
        LEFT -> X neg
        PG UP -> Z pos
        PG DOWN -> Z neg
        '''
        Scene.keyboard(self, event)

        if event.key == pygame.K_RIGHT:
            self.diamond.M = np.matmul(self.diamond.M, rotationMatrixY(math.pi/8))
            self.diamond.draw()

        elif event.key == pygame.K_LEFT:
            self.diamond.M = np.matmul(self.diamond.M, rotationMatrixY(-math.pi/8))
            self.diamond.draw()

        elif event.key == pygame.K_UP:
            self.diamond.M = np.matmul(self.diamond.M, rotationMatrixX(math.pi/8))
            self.diamond.draw()

        elif event.key == pygame.K_DOWN:
            self.diamond.M = np.matmul(self.diamond.M, rotationMatrixX(-math.pi/8))
            self.diamond.draw()

        elif event.key == pygame.K_PAGEUP:
            self.diamond.M = np.matmul(self.diamond.M, rotationMatrixZ(math.pi/8))
            self.diamond.draw()

        elif event.key == pygame.K_PAGEDOWN:
            self.diamond.M = np.matmul(self.diamond.M, rotationMatrixZ(-math.pi/8))
            self.diamond.draw()

        elif event.key == pygame.K_w:
            self.diamond.M = np.matmul(self.diamond.M, translationMatrix([0, 1, 0]))
            self.diamond.draw()

        elif event.key == pygame.K_s:
            self.diamond.M = np.matmul(self.diamond.M, translationMatrix([0, -1, 0]))
            self.diamond.draw()

        elif event.key == pygame.K_d:
            self.diamond.M = np.matmul(self.diamond.M, translationMatrix([1, 0, 0]))
            self.diamond.draw()

        elif event.key == pygame.K_a:
            self.diamond.M = np.matmul(self.diamond.M, translationMatrix([-1, 0, 0]))
            self.diamond.draw()
        
        elif event.key == pygame.K_LSHIFT:
            self.diamond.M = np.matmul(self.diamond.M, translationMatrix([0, 0, 1]))
            self.diamond.draw()

        elif event.key == pygame.K_LCTRL:
            self.diamond.M = np.matmul(self.diamond.M, translationMatrix([0, 0, -1]))
            self.diamond.draw()


if __name__ == '__main__':
    # initialises the scene object
    # scene = Scene(shaders='gouraud')
    scene = JungleScene()

    # starts drawing the scene
    scene.run()