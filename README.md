# plithos

<p align="center" class="image-wrapper">
 <img src="https://raw.githubusercontent.com/dev-coop/plithos/master/docs/plithos.gif" alt="Plithos in action" width="320" height="320">
 <br>
 <i>plithos learning to find objective</i>
</p>

## Installation

### Mac

Install pygame requirements

    brew install sdl sdl_image sdl_mixer sdl_ttf portmidi hg

Clone this repo and move to the dir

    git clone git@github.com:dev-coop/plithos.git && cd plithos

Install python requirements

    pip install -r requirements.txt

Test it

    python src/run.py

OPTIONALLY [install cuDNN](http://deeplearning.net/software/theano/library/sandbox/cuda/dnn.html) if you have a discrete GPU


# Machine learning scoring

- Give 1 point for exploring some area that hasn't been explored in 1 min or something like that, diminishing returns
for places that have already been explored. So if you explore the same place, then wait 10 seconds, you get like 15% of
the reward. If you explore it immediately after you get a -1??
- Have a "goal area" where we think the objective may be, give + some points for going towards it???
- Reward for moving away from other drones??
- Penalize for moving out of the area?



- Mark "explored" areas in green and slowly turn back to black again
- Show sensor radius around drones


# Getting state

The state will be the entire map `(WIDTH, HEIGHT)` where:
 - 0 is unexplored, nothing there
 - 1 is a drone
 - 2 is the objective
 - < 0 is explored, but updated each tick. So -1 was just explored, -0.99 was explored 1 tick ago.. something like that



# Crazy ideas

 - Add a "objective movement predictor" that marks the most likely location of the objective. This predictor can change it's prediction based on given values like: current, wind, temperature, etc.


### Todo:
- [ ] Draw a map with drones; show x, y, z
- Add multiple kinds of drones
    - [ ] Speedy
    - [ ] Weak
    - [ ] Strong
    - [ ] Slow
- Scenarios like:
    - [ ] Drifting in water
    - [ ] Stuck on a steep cliff
    - [ ] Multiple drones losing sensors
    - [ ] Multiple drones being destroyed in an area (hopefully they learn to avoid that area? fires?)
    - [ ] Saving multiple people
    - [ ] Allow objective to wander... and to wander OFF the map!
