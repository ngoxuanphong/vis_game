## Installation

### **Install vis_game library**

To install the base Gym library, use `pip install gym`.

To upgrade vis_game library, use `pip install --upgrade vis_game`.

### **Clone github**

`git clone http://ngoxuanphong/vis_game.git`

## API

**GAME:** `TLMN`, `TLMN_V2`, `Splendor`, `Splendor_v2`, `Catan`, `Catan_v2`, `Sushigo`, `MachiKoro`, `Sheriff`, `Century`

Creating environment instances and interacting with them is very simple

- here's an example using the "TLMN" environment:

```python
import numpy as np
from vis_game.base.TLMN.env import getValidActions, getActionSize, getReward, getStateSize, numba_main_2, normal_main_2, normal_main
from numba import njit
@njit()
def test(p_state, temp_file, per_file):
    arr_action = getValidActions(p_state)
    arr_action = np.where(arr_action == 1)[0]
    act_idx = np.random.randint(0, len(arr_action))
    return arr_action[act_idx], temp_file, per_file

numba_main_2(test, [0], 1000)
```

`getValidActions`: Return possible actions

`getActionSize`: Return amount action in game

`getStateSize`: Return amount of np array observation state of agent

`getReward`: Return 0 if game not ended, 1 if agent win, -1 if agen lose

**Runcode**

'numba_main_2(function_of_agent, agent_data, total_of_match)'.
  - `function_of_agent`: support numba library(function)
  - `agent_data`: support numba library(list, numba List, np array...)
  - `total_of_match`: total match run game(int)

'normal_main_2(function_of_agent, agent_data, total_of_match)'.
  - `function_of_agent`: function
  - `agent_data`: data of agent
  - `total_of_match`: total match run game(int)
