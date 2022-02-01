import numpy as np
import matplotlib.pyplot as plt

#Helper functions to calculate distances
def calcdistsqr(v):
    """Get euclidean distance^2 of v"""
    return np.sum(v**2)

def calcdist(v):
    """Get euclidean distance of v"""
    return np.sqrt(np.sum(v**2))


class Agent:
    def __init__(self,age,food,position,speed,lastbreed):
        """
        age = age of agent in iterations
        food = how much food the agent has 'inside' (0=empty, 1=full)
        position = x,y position of the agent
        speed = how fast it can move (tiles/iteration)
        lastbreed = how long ago it last reproduced (iterations)
        """
        self.food = food
        self.age = age
        self.position = position
        self.speed = speed
        self.lastbreed = lastbreed
      
    def breed(self):
        """
        This will either return None, or a new agent object
        """
        new_agent = None
        if (self.lastbreed>self.breedfreq) and (self.food>self.breedfood):
            self.lastbreed = -1
            new_agent = type(self)(0,self.food/2,self.position,self.speed,10)
            self.food = self.food/2
        self.age+=1
        self.lastbreed+=1
        return new_agent
       
    def move(self,env):
        pass
    
    def eat(self,env,agents):
        pass
    
    def summary_vector(self):
        return [self.position[0],self.position[1],type(self)==Rabbit]
    
class Rabbit(Agent):
    vision = 5 #how far it can see around current tile
    breedfreq = 20 #how many iterations have to elapse between reproduction events
    breedfood = 20 #how much food has to be eaten to allow reproduction
    maxage = 40 #how long do they live
    
    def __init__(self,age,food,position,speed,lastbreed):
        super().__init__(age,food,position,speed,lastbreed)
        self.eaten = False
        
    def move(self,env):
        """
        rabbit movement:
         - if current cell has no food...
            - will move towards cells with more food
         - DOESN'T move away from nearby foxes
        """
        if env.get_food(self.position)==0:
            food_position = env.get_loc_of_grass(self.position,self.vision) #get the x,y location of nearby food (if any)
            if food_position is not None:
                relative_food_position = food_position - self.position
                if calcdistsqr(relative_food_position)<self.speed**2: #if distance to the food < how far we can go, then
                    self.position = food_position

                else:
                    vect = relative_food_position / calcdist(relative_food_position)
                    self.position = self.position + vect * self.speed
            else:
                #no food in range, pick a random direction...
                d = np.random.rand()*2*np.pi #pick a random direction
                delta = np.round(np.array([np.cos(d),np.sin(d)])* self.speed)

                self.position = self.position + delta
                
        #ensures it's in the environment and rounds to nearest cell
        env.fix_position(self.position)
        
    def eat(self,env,agents):
        """
         - will eat if there's food at location
        """
        if env.get_food(self.position)>0:
            env.reduce_food(self.position)
            self.food += 1
        else:
            self.food -= 1
            
    def draw(self):
        plt.plot(self.position[0],self.position[1],'yx',mew=3)
        
    def die(self):
        """
        Returns true if it needs to expire
        """
        if self.food<=0: return True
        if self.age>self.maxage: return True
        if self.eaten: return True
        return False
        
class Fox(Agent):
    vision = 7 #how far it can see around current tile
    breedfreq = 10 #how many iterations have to elapse between reproduction events
    breedfood = 10 #how much food has to be eaten to allow reproduction
    maxage = 150 #how long do they live
    
    def get_nearby_rabbit(self,position,vision,agents):
        """
        helper function, given the list of agents, find the nearest rabbit, if within 'vision', else None.
        """
        #distances to dead rabbits, or foxes set to infinity.
        sqrdistances = np.sum((np.array([a.position if (type(a)==Rabbit) and (not a.die()) else np.array([-np.inf,-np.inf]) for a in agents])-position)**2,1)
        idx = np.argmin(sqrdistances)
        if sqrdistances[idx]<vision**2:
            return agents[idx]
        else:
            return None
    
    def eat(self,env,agents):
        """     
        Will eat nearby rabbits
        """
        near_rabbit = self.get_nearby_rabbit(self.position,self.vision,agents) #get the x,y location of nearby rabbit (if any)
        if near_rabbit is not None:
            relative_food_position = near_rabbit.position - self.position
            dist = calcdist(relative_food_position)
            if dist<self.speed: #if distance to the food < how far we can go, then
                # probability that fox will kill rabbit is ratio of speed to distance
                kill_prob = 1 - (dist / self.speed)
                if kill_prob>np.random.rand():
                    self.position = near_rabbit.position
                    near_rabbit.eaten = True
                    self.food+=2#near_rabbit.food/2

        #ensures it's in the environment and rounds to nearest cell
        env.fix_position(self.position)
        
    def move(self,env):
        """
         - 
        """
        d = np.random.rand()*2*np.pi #pick a random direction
        delta = np.round(np.array([np.cos(d),np.sin(d)])* self.speed)
        self.position = self.position + delta
            
    def draw(self):
        plt.plot(self.position[0],self.position[1],'sb',markersize=6)
        
    def die(self):
        """
        Returns true if it needs to expire
        """
        
        if self.food<=0: return True
        if self.age>self.maxage: return True
        return False
    
    