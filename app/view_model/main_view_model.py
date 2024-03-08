class Model:
    pass


class ReactiveModel:
    __attribs = Model()  # attribs
    __cbs = Model()  # callbacks

    def __init__(self):
        super().__init__()

    def __getattr__(self, attr: str):
        if hasattr(self.__attribs, attr):
            return getattr(self.__attribs, attr)

    def __setattr__(self, attr: str, value):
        # print("Yep", attr, value)
        setattr(self.__attribs, attr, value)
        if hasattr(self.__cbs, attr):
            cbs: list = getattr(self.__cbs, attr)
            for cb in cbs:
                cb(value)

    def on_change(self, attrib: str, cb):
        if not hasattr(self.__cbs, attrib):
            setattr(self.__cbs, attrib, [])
        cbs: list = getattr(self.__cbs, attrib)
        cbs.append(cb)

    def off_change(self, attrib: str, cb):
        if hasattr(self.__cbs, attrib):
            cbs: list = getattr(self.__cbs, attrib)
            try:
                cbs.remove(cb)
            except ValueError:
                pass


class MainViewModel(ReactiveModel):
    state: str
    command: str
    tracking_info: dict


view_model = MainViewModel()
view_model.state = "menu"
