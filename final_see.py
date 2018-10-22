import arcade
import random
import time
import pygame
import sys
from subprocess import call

SPRITE_SCALING = 0.025
BOX_SCALING = 0.1
APPLE_SCALING = 0.05
GHOST_SCALING = 0.07

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

NUMBER_OF_COINS = 25 #Also change in self.coins_left
NUMBER_OF_GHOSTS = 15

MOVEMENT_SPEED = 5

GAME_RUNNING = 0
GAME_OVER = 1
GAME_WON = 2

INVISIBLE_BOO = 0
VISIBLE_BOO = 1

def locator(x_inp, y_inp):  

    x_cord = (x_inp) * 31 + x_inp + 1
    y_cord = (y_inp) * 31 + y_inp + 1

    return x_cord, y_cord

def playMusic():

    pygame.mixer.init()
    pygame.mixer.music.load("mainMusic.mp3")
    pygame.mixer.music.play()

def winMusic():

    pygame.mixer.init()
    pygame.mix.music.load("tada.mp3")
    pygame.mixer.music.play()

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        """
        super().__init__(width, height)
        # Sprite lists
        self.all_sprites_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.wall_list = None
        self.physics_engine = None

        self.current_state = GAME_RUNNING
        self.boo_state = INVISIBLE_BOO

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.coins_left = 25
        self.player_sprite = arcade.Sprite("pumpkin.png", SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 64


        self.boo_sprite = arcade.Sprite("boo.png", 1)
        self.boo_sprite.set_position(500,500)

        self.game_over_sprite = arcade.Sprite("game_over.png",1)
        self.game_over_sprite.set_position(500,500)

        

#MAPPING START ###################################################


        mapArray = []

        mapFile = open("map.txt","r")

        content = mapFile.readline()

        line = 1

        while content:

            mapArray.append(content)

            content = mapFile.readline()

        """ SET UP THE MAIN MAP FILE """
        MapFinal = []
        for row in range(32):
            MapRow = ['']
            for column in range(24):
                MapColumn = ['']
                MapRow.append(MapColumn)
            MapFinal.append(MapRow)

        for a in range(32):
            for b in range(24):
                if mapArray[a][b] == "w":
                    MapFinal[a][b] = "w"
                elif mapArray[a][b] == "t":
                    MapFinal[a][b] = "t"
                elif mapArray[a][b] == "-":
                    MapFinal[a][b] = "-"


        for x in range(32):
            for y in range(24):

                if MapFinal[x][y] == 'w':
                    x_block, y_block = locator(x,y)
                    wall = arcade.Sprite("box.png", BOX_SCALING)
                    wall.center_x = x_block
                    wall.center_y = y_block
                    self.wall_list.append(wall)

        ## MAPPING END #############################################

        # -- Randomly place coins where there are no walls
        # Create the coins
        for i in range(NUMBER_OF_COINS):

            coin = arcade.Sprite("apple.png", APPLE_SCALING)

            # --- IMPORTANT PART ---

            # Boolean variable if we successfully placed the coin
            coin_placed_successfully = False

            # Keep trying until success
            while not coin_placed_successfully:
                # Position the coin
                coin.center_x = random.randrange(SCREEN_WIDTH)
                coin.center_y = random.randrange(SCREEN_HEIGHT)

                # See if the coin is hitting a wall
                wall_hit_list = arcade.check_for_collision_with_list(coin, self.wall_list)

                # See if the coin is hitting another coin
                coin_hit_list = arcade.check_for_collision_with_list(coin, self.coin_list)

                if len(wall_hit_list) == 0 and len(coin_hit_list) == 0:
                    # It is!
                    coin_placed_successfully = True

            # Add the coin to the lists
            self.coin_list.append(coin)


        #Create the ghosts
        for i in range(NUMBER_OF_GHOSTS):

            ghost = arcade.Sprite("ghost.png", GHOST_SCALING)
            ghost_placed_successfully = False
            while not ghost_placed_successfully:
                ghost.center_x = random.randrange(SCREEN_WIDTH)
                ghost.center_y = random.randrange(SCREEN_HEIGHT)

                wall_hit_list = arcade.check_for_collision_with_list(ghost, self.wall_list)
                coin_hit_list = arcade.check_for_collision_with_list(ghost, self.coin_list)
                ghost_hit_list = arcade.check_for_collision_with_list(ghost, self.ghost_list)
                player_hit_list = arcade.check_for_collision(ghost, self.player_sprite)
                
                if len(wall_hit_list)==0 and len(coin_hit_list)==0 and len(ghost_hit_list)== 0 and (player_hit_list)==0:
                    ghost_placed_successfully = True

            self.ghost_list.append(ghost)



            # --- END OF IMPORTANT PART ---

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Check what is the current state
        if self.current_state == GAME_OVER:
            # Draw game over screen.
            self.draw_game_over()
        elif self.current_state == GAME_WON:
            self.draw_game_won()
        else:
            # Draw all the sprites.
            self.wall_list.draw()
            self.coin_list.draw()
            self.ghost_list.draw()
            self.player_sprite.draw()
            output = f"Score: {self.score}"
            arcade.draw_text(output, 900, 600, arcade.color.WHITE, 14)

        if self.boo_state == VISIBLE_BOO:
            self.draw_boo()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if self.current_state == GAME_RUNNING:
            if key == arcade.key.UP:
                self.player_sprite.change_y = MOVEMENT_SPEED
            elif key == arcade.key.DOWN:
                self.player_sprite.change_y = -MOVEMENT_SPEED
            elif key == arcade.key.LEFT:
                self.player_sprite.change_x = -MOVEMENT_SPEED
            elif key == arcade.key.RIGHT:
                self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_state == GAME_OVER:
            self.setup()
            self.current_state = GAME_RUNNING

    def update(self, delta_time):
        """ Movement and game logic """
        coins_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        ghosts_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.ghost_list)

        for coin in coins_hit_list:
            coin.kill()
            self.coins_left-=1
            self.score+=1

        for ghost in ghosts_hit_list:
            ghost.kill()
            self.boo_state = VISIBLE_BOO
            self.score-=2
            if sys.platform == 'darwin':
                call(["afplay","ScreamSound.mp3"])
            else:
                arcade.sound.play_sound("ScreamSound.mp3")

        if self.score < 0:
            self.current_state = GAME_OVER

        if self.coins_left == 0:
            self.current_state = GAME_WON

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

    def draw_game_over(self):
        self.game_over_sprite.draw()
        output = "GAME OVER"
        arcade.draw_text(output, 350, 450, arcade.color.WHITE, 54)

    def draw_game_won(self):
        output = "YOU WON!"
        arcade.draw_text(output, 350, 300, arcade.color.WHITE, 54)

    def draw_boo(self):
        self.boo_sprite.draw()
        
        self.boo_state = INVISIBLE_BOO
        self.boo_sprite.kill()

def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    playMusic()
    arcade.run()


if __name__ == "__main__":
    main()
