from dataclasses import dataclass

@dataclass
class ButtonMessage:
    '''
    example:
        btn = ButtonMessage('navigator', 'https://mixin.one', '#ABABAB')
    '''
    label: str
    action: str
    color: str

@dataclass
class StickerMessage:
    name: str
    album_id: str
    sticker_id: str

@dataclass
class PictureMessage:
    '''
        {
            "attachment_id": "Read From POST /attachments",
            "mime_type": "image/jpeg",
            "width": 1024,
            "height": 1024,
            "size": 1024,
            "thumbnail": "base64 encoded"
        }
    '''
    attachment_id: str
    mime_type: str
    width: int
    height: int
    size: int
    thumbnail: str

@dataclass
class AudioMessage:
    '''
    {
        "attachment_id": "Read From POST /attachments",
        "mime_type": "audio/ogg",
        "size": 1024,
        "duration": 60,
        "waveform": "QIQQSA...AAIAA"
    }
    '''
    attachment_id: str
    mime_type: str
    size: int
    duration:int
    waveform: str

@dataclass
class VideoMessage:
    '''
     {
        "attachment_id": "Read From POST /attachments",
        "mime_type": "video/mp4",
        "width": 1024,
        "height": 1024,
        "size": 1024,
        "duration": 60,
        "thumbnail": "base64 encoded"
    }
    '''
    attachment_id: str
    mime_type: str
    width: int
    height: int
    size: int
    duration: int
    thumbnail: int

@dataclass
class ContactMessage:
    '''
    {
        "user_id": "UUID"
    }
    '''
    user_id: str

@dataclass
class CardMessage:
    '''
    {
        "app_id": "7404c815-0393-4ea3-b9f2-b08efe4c72da",
        "icon_url": "https://mixin.one/assets/98b586edb270556d1972112bd7985e9e.png",
        "title": "Mixin",
        "description": "Hello World.",
        "action": "https://mixin.one",
        "shareable": true
    }
    '''
    app_id: str
    icon_url: str
    title: str
    description: str
    action: str
    shareable: bool

@dataclass
class FileMessage:
    '''
    {
        "attachment_id": "Read From POST /attachments",
        "mime_type": "application/pdf",
        "size": 1024,
        "name": "2020-12-12.pdf"
    }
    '''
    attachment_id: str
    mime_type: str
    size: int
    name: str

@dataclass
class LiveMessage:
    '''
    {
        "width": 650,
        "height": 366,
        "thumb_url": "https://mixin.one/logo.png",
        "url": "https://mixin.one/live.m3u8"
    }
    '''
    width: int
    height: int
    thumb_url: str
    url: str

@dataclass
class LocationMessage:
    '''
    {
        "longitude": 126.5893955829421,
        "latitude": 53.47845177824066,
        "name": "China",
        "address": "中国北京市"
    }
    '''
    longitude: float
    latitude: float
    name: str
    address: str

@dataclass
class TransferMessage:
    '''
    {
        "type": "transfer",
        "snapshot_id": "ab56be4c-5b20-41c6-a9c3-244f9a433f35",
        "opponent_id": "a465ffdb-4441-4cb9-8b45-00cf79dfbc46",
        "asset_id": "43d61dcd-e413-450d-80b8-101d5e903357",
        "amount": "-10",
        "trace_id": "7c67e8e8-b142-488b-80a3-61d4d29c90bf",
        "memo": "hello",
        "created_at": "2018-05-03T10:08:34.859542588Z"
    }
    '''

    type: str
    snapshot_id: str
    opponent_id: str
    asset_id: str
    amount: str
    trace_id: str
    memo: str
    created_at: str
