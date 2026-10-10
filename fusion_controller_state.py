class ControllerState:

    def __init__(self):

        self.current_mode = None
        self.current_performance = None
        self.current_parts = {}
        self.current_song_programs = {}
        self.active_notes = set()
        self.pending_reload = False
        self.reload_wait_announced = False

state = ControllerState()
