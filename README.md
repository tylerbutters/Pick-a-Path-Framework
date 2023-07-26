# Pick-a-Path-Framework
## Made: July 2023 in 1 Week

## Preperation
Make a copy of this sheet and start writing your story: <br />
https://docs.google.com/spreadsheets/d/1ZtABSsgwkZ06acGfN6tVhi9x9v30DaQ7U02MkXr2eI4/edit?usp=sharing <br />
All the entities are linked by an ID. They all start with the first letter of their class name followed by a number of your choosing <br />
Consequence is the exception, it's ID starts with an 'O'. So all the IDs are: Nodes: N, Choice: C, Requirement: R, Conseqeunce: O <br />
Once you're done download each sheet as a .csv and rename it to just the object name in lowercase: "nodes.csv" <br />
You will also need a .csv file called "saves.csv", you can download the one in the google sheet or make your own, they can be blank. <br />
Put them all in a folder and name it whatever you want, then place the folder into the project. <br />
Go into the "FileManager.py" file and change the "STORY_NAME" variable to the name of your folder. <br />
You can have multiple stories in the project and all you need to do is switch the folder name. <br />

## Nodes
To set the starting node, make the ID "<START>" <br />
To set the end node, make the ID "<END>" <br />
The name column is just so you know what the node's story is. It doesn't affect the code. <br />
The description will display when you first visit a node but the revisited description will display anytime you come back. <br />
It should just give you a small summary of information or something like: "You went back." <br />
Type the character '\' whenever you want to make a newline. <br />
The you can only have a target node or a list of choices, not both. <br />
You can only have 1 target node but can have an unlimited amount of choices. <br />
Keep all the choices in the same cell but seperate them by a '|' like this: "C33|C53|C64"
The target node is for if you just want to print the description then navigate to a new node. <br />
If you navigate back from the node you came from it's called a "Rebound Node" <br />
If you navigate to a new node it's a "Continuation Node" <br />

## Choices
Unlike a node, the choice's name is important. It's what will be displayed on the screen. <br />
A choice has a visibility requirement, a navigation requirement, a consequence and a true and false node. <br />
You must have a true node but you can leave requirement and consequence empty. <br />
If you have a navigation requirement then you must have both a true and a false target node. <br />
If your navigation requirements are met then it will navigate to the true not, else it will go to the false node. <br />
For example: If there's a choice to open a door, with the navigation requirement being you need a key. <br />
If you don't have a key it will navigate to the false node: "You pull on the door, it's locked" <br />
If you DO have a key it will navigate to the true node: "You open the door" <br />
The the visibility requirement determines wether the choice displays to the user. <br />
For example, if the requirement is that you need to have visited Node: N13, and you haven't then it won't show up. <br />
But once you do visit that node, then the choice will show up. <br />

## Requirements
Each requirement has a list of items, node visits that need to be met. <br />
You can have an unlimited number of these things or you can leave them blank. But each thing must be seperated by '|'<br />
Node visits will check your node history to see if you've visited the node. <br />
Items will check your inventory. Just write in whatever item they need, like: "hammer" <br />

## Consequences
A consequence will apply whenever you navigate to the true node, even if you don't have a requirement. <br />
It will remove or add any items to your inventory and/or remove the choice from your options. <br />
All you need to write is a '+' or '-' at the beginning of the item. <br />
If it's a '+' it will add it to your inventory, a '-' will take it away: "+hammer" <br />
You can have an unlimited number of these and they also need to be seperated by a '|' <br />
You can also remove the choice once it has been made by writing true or false <br />
If you leave this area blank it will be false by default. <br />