import numpy as np
from ecolab3.agents import Rabbit, Fox
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def run_ecolab(env,agents,Niterations=10000,earlystop=True):
    """
    Run ecolab with some selection of parameters.
    """

    record = []
    for it in range(Niterations):
        #for each agent, apply rules (move, eat, breed)
        for agent in agents:
            agent.move(env)
            agent.eat(env,agents)
            a = agent.breed()
            if a is not None: agents.append(a)

        #removed dead agents
        agents = [a for a in agents if not a.die()]

        #grow more grass
        env.grow()

        #record the grass and agent locations (and types) for later plotting & analysis
        record.append({'grass':env.grass.copy(),'agents':np.array([a.summary_vector() for a in agents])})

        #stop early if we run out of rabbits or foxes
        if earlystop:
            nF = np.sum([type(a)==Fox for a in agents])
            nR = np.sum([type(a)==Rabbit for a in agents])        
            if (nF<1): break
            if (nR<1): break
    return record

def draw_animation(fig,record):
    """
    Draw the animation for the content of record
    """
    if len(record)==0: return None

    im = plt.imshow(np.zeros_like(record[0]['grass']), interpolation='none', aspect='auto', vmin=0, vmax=3, cmap='gray')
    ax = plt.gca()

    foxes = ax.plot(np.zeros(100),np.zeros(100),'bo',markersize=10)
    rabbits = ax.plot(np.zeros(100),np.zeros(100),'yx',markersize=10,mew=3)

    def animate_func(i):
        im.set_array(record[i]['grass'])
        ags = record[i]['agents']
        if len(ags)==0:
            rabbits[0].set_data([],[])
            foxes[0].set_data([],[])
            return
        coords = ags[ags[:,-1].astype(bool),0:2]
        print(coords[:,1],coords[:,0])
        rabbits[0].set_data(coords[:,1],coords[:,0])
        coords = ags[~ags[:,-1].astype(bool),0:2]
        print(coords[:,1],coords[:,0])
        foxes[0].set_data(coords[:,1],coords[:,0])
        #return [im]#,rabbits,foxes]


    anim = animation.FuncAnimation(
                                   fig, 
                                   animate_func, 
                                   frames = len(record),
                                   interval = 1000 / 20, repeat=False # in ms
                                   )
    return anim