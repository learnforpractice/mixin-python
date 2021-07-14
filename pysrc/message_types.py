from dataclasses import dataclass

@dataclass
class Button:
    '''
    example:
        btn = Button('navigator', 'https://mixin.one', '#ABABAB')
    '''
    label: str
    action: str
    color: str
