from pyfdl import Header, FramingIntent, Context, CanvasTemplate


class FDL:
    def __init__(self, header: Header = None):
        if not header:
            header = Header()

        self.header = header
        self.framing_intents = []
        self.contexts = []
        self.canvas_templates = []

    def to_dict(self) -> dict:
        data = self.header.to_dict()
        data['framing_intents'] = [fi.to_dict() for fi in self.framing_intents]
        data['contexts'] = [ctx.to_dict() for ctx in self.contexts]
        data['canvas_templates'] = [template.to_dict() for template in self.canvas_templates]

        return data

    def __str__(self) -> str:
        return str(self.to_dict())

    @staticmethod
    def from_object(raw: dict):
        fdl = FDL()
        fdl.header = Header.from_dict(raw)
        fdl.framing_intents = [FramingIntent.from_dict(item) for item in raw.get('framing_intents', [])]
        fdl.contexts = [Context.from_dict(item) for item in raw.get('contexts', [])]
        fdl.canvas_templates = [CanvasTemplate.from_dict(item) for item in raw.get('canvas_templates', [])]

        return fdl
