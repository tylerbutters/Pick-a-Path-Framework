# Pick-a-Path-Framework

## Preperation
Make a copy of this sheet and start writing your story: <br />
https://docs.google.com/spreadsheets/d/1ZtABSsgwkZ06acGfN6tVhi9x9v30DaQ7U02MkXr2eI4/edit?usp=sharing <br />
Once you're done download each sheet as a .csv and rename it to just the object name in lowercase: "nodes.csv" <br />
You will also need a .csv file called "saves.csv", you can download the one in the google sheet or make your own, they can be blank. <br />
Put them all in a folder and name it whatever you want, then place the folder into the project. <br />
Go into the "FileManager.py" file and change "FILE_DIRECTORY" to the name of your folder. <br />
You can have multiple stories in the project and all you need to do is switch the folder name. <br />

## Nodes
To set the starting node, make the ID "<START>" <br />
To set the end node, make the ID "<END>" <br />
The name column is just so you know what the node's story is. It doesn't affect the code. <br />
The description will display when you first visit a node but the revisited description will display anytime you come back. <br />
It should just give you a small summary of information or something like: "You went back." <br />
The fifth column can either be a node or a list of choices. <br />
You can only have 1 target node but can have an unlimited amount of choices.
The target node is for if you just want to print the description then navigate to a new node. <br />
If you navigate back from the node you came from it's called a "Rebound Node" <br />
If you navigate to a new node it's a "Continuation Node" <br />

## Choices
Unlike a node, the choice's name is important. It's what will be displayed on the screen. <br />
A choice has a requirement, consequence and target nodes. <br />
You must have a target node but you can leave requirement and consequence empty. <br />
If you have a requirement then you must have both a true and a false target node. <br />
If your requirements are met then it will navigate to the true not, else it will go to the false node. <br />
For example: If there's a choice to open a door, with the requirement being you need a key. <br />
If you don't have a key it will navigate to the false node: "You pull on the door, it's locked" <br />
If you DO have a key it will navigate to the true node: "You open the door" <br />

## Requirements
Each requirement has a list of items, node visits and choices that need to be met. <br />
You can have an unlimited number of objects and they can be put in any order but it's recommended to place them: <br />
Items, Node visits, choices. <br />
Node visits and choices will check your node and choice histories to see if you've visited or made the choice. <br />
Items will check your inventory. Just write in whatever item they need, like: "hammer" <br />

## Consequences
A consequence will apply whenever you navigate to the true node, even if you don't have a requirement. <br />
It will remove or add any items to your inventory and/or remove the choice from your options. <br />
All you need to write is a '+' or '-' at the beginning of the item. <br />
If it's a '+' it will add it to your inventory, a '-' will take it away: "+hammer" <br />
You can have an unlimited number of these and they can be in whatever order. <br />
You can also remove the choice once it has been made by writing true or false <br />
If you leave this area blank it will be false by default. <br />
