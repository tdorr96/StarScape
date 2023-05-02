# StarScape

Game written in Python and PyQt, taking inspiration from Stardew Valley and Runescape.  

![Screenshot 1](/images/screenshots/sample1.png)  
![Screenshot 2](/images/screenshots/sample2.png)  
![Screenshot 3](/images/screenshots/sample3.png)  
![Screenshot 4](/images/screenshots/sample4.png)  

## Setup
Only two libraries are necessary. In a new virtual environment run  

<code>pip install PyQt5</code>  
<code>pip install regex</code>  

## Run
To start the game,  

<code>python game.py</code>

## Playing
The game is primarily interacted with by pressing keys and clicking. The status information displayed under
the map will output relevant information, if something happened (you gained a level), or you can't do something
(you don't have the right level tool/skill for an interaction).
* To move the player, press the arrow keys.
* To interact with something on the map, e.g. a tree or a shopkeeper, click on it.
* To view information about a skill, click it in the bottom left corner of the window.
* You can use items on one another in the inventory. E.g. light a log by clicking a tinderbox
to select it and then clicking a log; or fletch a bow by using a knife on a log.
* You can enter new areas by clicking on relevant tiles (e.g. ladders or cave entrances).
* When in a shop or bank mode, you can right-click to deposit/withdraw/buy/sell certain amounts.
* Every shop is unique - each shopkeeper keeps their own shop stock.
* There is one bank across the whole game - every bank chest interfaces to the same bank.
* You can close displays (e.g. shop interfaces or skill information displays) either by pressing
ESC or the close button.

## Work In Progress
* <b> Smithing skill</b>: Turn ores into bars at a furnace, then use those bars at an anvil with a hammer to make items like swords or arrows tips.
* <b>Combat skill</b>: Equip melee or ranged weapons to fight moving monsters. Weapons can be bought 
from shops, or made with smithing/fletching.
* <b> Thieving skill</b>: Thieve gold from NPCs or items from stalls and shopkeepers.
* <b> Improve shop mechanics </b>: Design shops to have a fixed set of items that they can stock (e.g. cannot buy/sell logs from/to a blacksmith); give stocked items a base amount and base price, so if you oversell items will depopulate from the stock after a certain amount of game ticks, and the sell price decreases as you sell past the base amount.
* <b> UI </b>: make prettier!
* <b> Executable package </b> and <b> multiplayer</b> over a local network.