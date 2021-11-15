import jsonmerge

class Context:
    def __init__(self):
        self.contextMap = []

    def get_all(self):
        return self.contextMap

    def update(self, entities):
        if len(self.contextMap) == 0:
            self.set_all(entities)
        else:
            for new_entity in entities:
                not_found = True
                for old_entity in self.contextMap:
                    if old_entity["id"] == new_entity["id"]:
                        self.contextMap.remove(old_entity)
                        try:
                            self.contextMap.append(jsonmerge.merge(old_entity,new_entity))
                        except:
                            self.contextMap.append(new_entity)
                        not_found = False
                        break
                if not_found == True:
                    self.contextMap.append(new_entity)

    def set_all(self, entities):
        self.contextMap.clear()
        for new_entity in entities:
            self.contextMap.append(new_entity)
