import numpy as np
import matplotlib.pyplot as plt

#helper function
def argmax_2darray(a):
    """
    Returns the maximum location in a n-d array
    """
    return np.unravel_index(a.argmax(), a.shape)

class Environment:
    def __init__(self,shape=[40,40],startgrass=2,maxgrass=5,growrate=40):
        """
        Create the environment
        Parameters:
         - shape = shape of the environment
         - startgrass = initial amount of grass
         - maxgrass = maximum amount of grass allowed in each tile
         - growrate = number of tiles which get extra grass each iteration
        """
        self.maxgrass = 5 #maximum it can grow to
        self.growrate = 40 #how many new items of food added per step
        self.shape = np.array([40,40]) #shape of the environment
        self.grass = np.full(self.shape,startgrass) #2*np.trunc(np.random.rand(*self.shape)*2)+2 #initial grass
        
    def get_food(self,position):
        """
        Returns the amount of food at position
        """
        return self.grass[int(position[0]),int(position[1])]
    
    def reduce_food(self,position,amount=1):
        """
        Reduce the amount of food at position by amount
        (note, doesn't check this doesn't go negative)
        """
        self.grass[int(position[0]),int(position[1])]-=amount
    
    def get_loc_of_grass(self,position,vision):
        """
        This finds the location of the cell with the maximum amount of food near 'pos',
        within a circle of 'vision' size.
        For example env.get_dir_of_food(np.array([3,3]),2)
        if two or more cells have the same food then it will select between them randomly.
        """
        
        #we temporarily build a new datastructure to look for the largest grass in with a
        #strip/boundary around the edge of zero food. This feels like the simplest code
        #to solve the edge case problem, but is quite a slow solution.
        boundary = 10
        pos = position + boundary
        grasswithboundary = np.zeros(np.array(self.grass.shape)+boundary*2)
        grasswithboundary[boundary:-boundary,boundary:-boundary] = self.grass
        #we search just a circle within 'vision' tiles of 'pos' (these two commands build that search square)
        searchsquare = grasswithboundary[int(pos[0]-vision):int(pos[0]+vision+1),int(pos[1]-vision):int(pos[1]+vision+1)]
        searchsquare[(np.arange(-vision,vision+1)[:,None]**2 + np.arange(-vision,vision+1)[None,:]**2)>vision**2]=-1
        #this returns the location of that maximum food (with randomness added to equally weight same-food cells)         
        if np.all(searchsquare<=0): return None #no food found
        return argmax_2darray(searchsquare+0.01*np.random.rand(vision*2+1,vision*2+1))+position-vision
        
    def fix_position(self,position):
        """
        Alters the position array in-place to be within the environment & rounded to nearest tile.
        (doesn't return anything)
        """
        position[:] = np.round(position)
        if position[0]<0: position[0]=0
        if position[1]<0: position[1]=0
        if position[0]>self.shape[0]-1: position[0]=self.shape[0]-1
        if position[1]>self.shape[1]-1: position[1]=self.shape[1]-1
            
    def get_random_location(self):
        """
        Returns a random location in the environment.
        """
        return np.random.randint([0,0],self.shape)
    
    def get_random_bias_location(self):
        """
        Returns a random location in the environment with a bias towards the 'top'.
        """
        if np.random.rand()<0.4:
            s = self.shape.copy()
            s[0]=int(s[0]/5)
            p = np.random.randint([0,0],s)
        else:
            p = np.random.randint([0,0],self.shape)
        
        return p
    
    
    def grow(self):
        """
        Adds more grass
        """
        for it in range(self.growrate):
            #loc = self.get_random_location()
            loc = self.get_random_bias_location()
            if self.grass[loc[0],loc[1]]<self.maxgrass:
                self.grass[loc[0],loc[1]]+=1

    def draw(self):
        """
        Plot the environment
        """
        plt.imshow(self.grass.T,cmap='gray')
        plt.clim([0,10])