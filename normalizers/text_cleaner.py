import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        # Remove leading/trailing whitespace per line
        text = '\n'.join([line.strip() for line in text.split('\n')])
        # Remove empty lines
        text = '\n'.join([line for line in text.split('\n') if line])
        return text.strip()
