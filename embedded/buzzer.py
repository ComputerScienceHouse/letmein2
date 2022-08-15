import pwmio

# from jingles import *

class Buzzer:
    # IDK where that 32768 number comes from. Probably a clock cycle or some shit.
    speaker_on = 2**15 # 32768 value is 50% duty cycle, a square wave.
    speaker_off = 0  # 0% duty cycle to stop the speaker

    # Define a list of tones/music notes to play.
    tone = {
        "C4" : 262,# - 0
        "D4" : 294,# - 1
        "E4" : 330,# - 2
        "F4" : 349,# - 3
        "G4" : 392,# - 4
        "A4" : 440,# - 5
        "B4" : 494,# - 6
        "C5" : 530,# - 7
    }

    def __init__(self, io_pin):
        self.buzzer = pwmio.PWMOut(io_pin, variable_frequency=True)

    def is_on(self):
        return self.buzzer.duty_cycle == self.speaker_on

    def on(self):
        self.buzzer.duty_cycle = self.speaker_on

    def is_off(self):
        return self.buzzer.duty_cycle == self.speaker_off

    def off(self):
        self.buzzer.duty_cycle = self.speaker_off

    # Select standard note
    def note(self, note):
        try:
            self.buzzer.frequency = self.tone[note]
        except KeyError:
            print("Unknown tone")

    # Set custom frequency
    def hz(self, hz):
        self.buzzer.frequency = hz

    async def play(self, sequence):
        pass #TODO (willnilges): Implement some cool way to play jingles
