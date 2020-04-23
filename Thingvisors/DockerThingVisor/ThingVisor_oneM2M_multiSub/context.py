import jsonmerge

class Context:
    def __init__(self):
        self.contextMap = []

    def get_all(self):
        return self.contextMap

    def update(self, entities):
        for new_entity in entities:
            for old_entity in self.contextMap:
                if old_entity["id"] == new_entity["id"]:
                    self.contextMap.remove(old_entity)
                    self.contextMap.append(jsonmerge.merge(old_entity,new_entity))
                    break
                else:
                    self.contextMap.append(new_entity)

    def set_all(self, entities):
        self.contextMap.clear()
        for new_entity in entities:
            self.contextMap.append(new_entity)
