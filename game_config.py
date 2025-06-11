class GameConfig:
    def __init__(self, lcl_args=None):
        self.duration_game = lcl_args.spieldauer if lcl_args and lcl_args.spieldauer else DURATION_GAME
        self.half_time_duration = lcl_args.halbzeitdauer if lcl_args and lcl_args.halbzeitdauer else HALF_TIME_DURATION
        self.fps = lcl_args.fps if lcl_args and lcl_args.fps else FPS_DEFAULT
        self.resolution = tuple(lcl_args.resolution) if lcl_args and lcl_args.resolution else RESOLUTION_DEFAULT
        self.camera_number = lcl_args.kameranummer if lcl_args and lcl_args.kameranummer else CAMERA_NUMBER_DEFAULT
        self.start_after = lcl_args.start_after if lcl_args and lcl_args.start_after else START_AFTER_DEFAULT
