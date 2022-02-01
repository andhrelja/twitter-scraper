import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_DIR = os.path.join(ROOT_DIR, 'input')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')

BASELINE_USER_IDS = os.path.join(INPUT_DIR, 'baseline-user-ids.json')
MISSING_USER_IDS = os.path.join(INPUT_DIR, 'missing-user-ids.json')
PROCESSED_USER_IDS = os.path.join(INPUT_DIR, 'processed-user-ids.json')

connections = {
    'icecream-1-IC': {
        'consumer_key': 'D1cFTRrLpIpJT136NfBo2A0u9' ,
        'consumer_secret': '3n6YDxzye30OahadlibPcZoh8H6yWB9FQ2x4JfNo4UR0k7m5xH',
        'access_key': '1169317946033922048-gnnApT1ZUfmoNeaTOykz9yM2FRsiWL',
        'access_secret': 'fN6l6WCjapzwWAW8dU0xiOFExhzeVOHnhmCJg3wwpSopv',
    },
    'icecream-2-IC2': {
        'consumer_key': 'm3NrMZ7PB4WVrDYAekQEr7mug',
        'consumer_secret': 'Pjl6UWbaye7PrP697nv5YHKngwcqnhVMAXdAtRCEJ02ppVXlVj',
        'access_key': '1316409694760689666-YSi25euJltCKcDWI1XeM24LUiK4uG5',
        'access_secret': 'cb3MG4RJeFkwt2FmHhgIH0V7OfijuN3MxXCcA1P3ntKlP',
    },
    'icecream-3-Carlos': {
        'consumer_key': 'r1tcZ5XPtMLzBhwNEZjhHb3vV',
        'consumer_secret': '7cGo82YQGOYGi3iJ1LJ9YeMP4GA6paIe2kabLLeicjMrUUhXxs',
        'access_key': '166318369-AhoqOVupAsjj0EnrVtHY6Pg3izqremykKLvZpjBV',
        'access_secret': 'kRCuZRn0j0Iowqd7VBCTQRgYuM5ZpwAc6ViEzmwJtFPcS',
    },
    'hrelja-1-andhrelja': {# AAAAAAAAAAAAAAAAAAAAABQAYwEAAAAAtdo8GPg%2BU8LkZch6B6kvkZAxTlE%3DxinBDLcs1zGPI4OEytAVCzYucBTAf8V4q0KBjEGWHtDqgUKAMn
        'consumer_key': 'Bf4MSXC7sM3f4uzLOTIJTwFUR' ,
        'consumer_secret': 'EEEW1hrODIsC4b9aSSA8yu0egSTap9TBr2DuuIMbkcLTEQkwSN',
        'access_key': '146153494-v4l1gPVW9dkYTIMPTSKgrF8Jg7PHnxQj5dYExVpU',
        'access_secret': 'xn9SuKIEgrkFzyc6pb3QakIWx9rJP1gHoj64JwG7gBPtW',
    },
    'hrelja-2-BioOrNotToBio': {# AAAAAAAAAAAAAAAAAAAAAIMFYwEAAAAAXfxTFhUw%2F3DpiNLBRXxGjkTslFI%3DyT7oCGI2H4Ovhikjy9zUQB2TGd90jc76fO9Avatz4uJV9o4f6w
        'consumer_key': 'KfvPOv5gzd4Wstehms12KwHHT' ,
        'consumer_secret': '0JCkSUP7VbjlK7hBBfxhxpzjSkfQfwuRHK4idEqOfZav8loAUm',
        'access_key': '1488520803033534466-qIqsR9jQ4kyn3ZC0ERuihpuBvFbQUq',
        'access_secret': 'mFfop6ca17HgOpRbMFqoSApOtkMlT2ITEVGX7AqSV0f8n',
    },
    'hrelja-3-KinderGartenRi': {# AAAAAAAAAAAAAAAAAAAAALQFYwEAAAAAK6xHNFNjs02d%2FgACwqjJxCcssZE%3DXOduVoQTyfqV0ycSXWtPTxKoWAGZtIKHGQVi07dMUC5DNszNj6
        'consumer_key': 'I7CJiw0SOzXaW8D28oYLYbDVd' ,
        'consumer_secret': 'WrTU9mm4QO1RFriMc4XCWhEVjf9XRCETcHPxZvv7I89wgjfMgq',
        'access_key': '1488523272891375621-y8ItLVJkeUmEZh4ZtUsWTgJ0ArRxAj',
        'access_secret': 'M4NzuVKkcFxXbNkoyxEmChQ9t4FLSkryTEORcuE8lsHOp',
    }
}
