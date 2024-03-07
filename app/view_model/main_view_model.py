from ..model.reactive_model import ReactiveModel


class MainViewModel(ReactiveModel):
    state: str
    command: str
    tracking_info: str

    def set_state(self, state: str):
        self.state = state

    def set_command(self, app_model_command: str):
        self.command = app_model_command

    def get_tracking_info(self) -> str:
        return self.tracking_info

    def set_tracking_info(self, tracking_info: str):
        self.tracking_info = tracking_info


view_model = MainViewModel()
view_model.state = "menu"
