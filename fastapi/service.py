from models import Tag

class Service:

    @staticmethod
    def create(tag: Tag):
        print(tag.tag)