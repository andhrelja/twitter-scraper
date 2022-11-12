from .tweets import tweets
from .tweets import stanza_supported_languages
from .tweets import classla_supported_languages

import os
import stanza
import classla

logging_level = 'ERROR'
stanza_model_dir = stanza.resources.common.DEFAULT_MODEL_DIR
classla_model_dir = classla.resources.common.DEFAULT_MODEL_DIR

for stanza_lang in stanza_supported_languages:
    if not os.path.exists(os.path.join(stanza_model_dir, stanza_lang)):
        stanza.download(stanza_lang, logging_level=logging_level)

for classla_lang in classla_supported_languages:
    if not os.path.exists(os.path.join(classla_model_dir, classla_lang)):
        classla.download(classla_lang, logging_level=logging_level)
