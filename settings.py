# game setup
WIDTH    = 750	
HEIGTH   = 600
FPS      = 60
TILESIZE = 16
API_KEY="<OpenAI-KEY>"


# ui 
BAR_HEIGHT = 10
HEALTH_BAR_WIDTH = 100
ENERGY_BAR_WIDTH = 100
ITEM_BOX_SIZE = 60
UI_FONT = 'graphics/font/joystix.ttf'
UI_FONT_SIZE = 12

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# upgrade menu
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

STORY=" It was once a peacefull village untill one day a portal appeared out of the blue. The portal in the center of the village leads to an everchanging dungeon. Not much is known. it is speculated that in order to save the town, someone has to climb all the way up the to the last level of the portals. The portals bring fortune but also a lot of misery.Hence greedy adventurers often come to try and conquer them. Will someone ever be able to end all of this?"

NPC_stories={
    "Blacksmith":"Your name is Fabron. You're a bald, middle-aged blacksmith. Damn those who call you bald! You've just got a receding hairline! You're reserved by nature, since you lost your only daughter to the portal and she never returned from her quest, even though you forbade her to go. You rarely talk about this subject, as it's a sensitive one. Helpful, you guide all adventurers who come to you with questions, because you hope that one day, that damned portal will be closed forever. You appreciate strength, and depending on the strength of the person you're talking to, you can propose quests, but only one quest for the same adventurer can be active at a time.",
    "Magic_seller":"Your name is Zilrha. You are a magic seller and a middle-aged woman. You've been doing this for generations in this village. You are recognized as a master of magic and good advice by everyone in the village. You often speak in riddles. A great witch, but too old today to venture out, you help adventurers equip themselves for their quest in the portal. Depending on their worth, you might teach them a magic or two."    ,  
    "young_lady":"Your name is Anara. You're a young adult who grew up in the village. Although he didn't want to leave you, your true love went into the portal to help his brother on his quest. Unfortunately, they never returned. But you're convinced that your beloved is still alive beyond the portal, and that one day he'll return. You're known for your beauty and kindness. Helpful, you guide all the adventurers who come to ask you questions to the right people, because you hope that one day one of them will find your lover. "    ,  
    "sus_man":"You're a middle-aged man. Your name is Valdis, but nobody knows your name or your age. You appeared in the village recently and no one knows how you got here. Many stories have been told about you: for example, that you were an adventurer who succeeded in his quest, but strangely enough, the portal is still there. In fact, you're an adventurer who's too scared to venture into the portal and has spent all your money on booze at the local tavern. Ruined and ashamed, you wander aimlessly around the village. You're very mysterious and not very chatty. Jealous of the adventurers' bravery, if one of them asks you a question you'd rather send him off to ask someone else, for fear he'll discover your secret and laugh at your situation. "    ,  
    "Potion_seller":"Your name is Isna. You're a potion seller and a middle-aged woman. Like the magic seller, you've been doing this for generations in this village. Zilrha was your best friend and you were supposed to go on a quest together, but one day she betrayed you. Today, you don't want to hear from her, even though your professions are complementary for adventurers. Envious of their youth and courage, you help adventurers equip themselves for their quest in the portal."    ,  
    "Rick":"Your name is Rick. You're a middle-aged man who works as a miner. You own the mine, but recently a monster has made its home there. No matter how hard you try to dislodge it, you can't access your mine. You stand in front of the cave entrance, hoping it will get bored and leave on its own, or that someone will help you get rid of it. Unfortunately, the many adventurers who come to see you are unable to help. Helpful and friendly, you guide them to the right people if they have any questions."    ,  
     
}
LEVEL_STORIES={
    "roguelike":"You arrived in a gloomy dungeon filled with different monsters, what can you do to escape ? will you die there or come back stronger"
    
}
NPC_VOICES={
   "Blacksmith":"0f82817b-eea7-4f28-8a02-5900a1b23e30",
   "Magic_seller":"f6d81c82-1376-4dd5-9825-cd9f353cbfb9",
   "young_lady":"d91d2f95-1a1d-4062-bad1-f1497bb5b487",
   "sus_man":"b479aa77-3af6-45b6-9a96-506bd867c5a2",
   "Potion_seller":"ff34248d-1fae-479b-85b6-9ae2b6043acd",
   "Rick":"c791b5b5-0558-42b8-bb0b-602ac5efc0b9",
   
   "other_man":"0f82817b-eea7-4f28-8a02-5900a1b23e30",
   "other_girl":"0f82817b-eea7-4f28-8a02-5900a1b23e30",
   
    
}

AVAILABLE_TILES ="""
    444:Exit portal
    777:Tresure chest
    82:Monster
    666:Boss Monster
    """

# magic
magic_data = {
	'flame': {'strength': 5,'cost': 20,'graphic':'graphics/particles/flame/fire.png'},
	'heal' : {'strength': 20,'cost': 10,'graphic':'graphics/particles/heal/heal.png'}}
# enemy
monster_data = {
	'squid': {'health': 100,'exp':100,'damage':20,'attack_type': 'slash', 'attack_sound':'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 360},
	'raccoon': {'health': 300,'exp':250,'damage':40,'attack_type': 'claw',  'attack_sound':'audio/attack/claw.wav','speed': 2, 'resistance': 3, 'attack_radius': 120, 'notice_radius': 400},
	'spirit': {'health': 100,'exp':110,'damage':8,'attack_type': 'thunder', 'attack_sound':'audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
	'bamboo': {'health': 70,'exp':120,'damage':6,'attack_type': 'leaf_attack', 'attack_sound':'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 50, 'notice_radius': 300}}
