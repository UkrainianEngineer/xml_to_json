import json
try:
    import xmltodict
except ImportError:
    print("Please install xmltodict.")

ROOT = "AppiumAUT"
APPLICATION = "XCUIElementTypeApplication"
WINDOW = "XCUIElementTypeWindow"
XCUI_PREFIX = "XCUI"


class XmlToJson:
    def __init__(self, filename):
        with open(filename) as fd:
            # Read XML into JSON.
            content = json.loads(
                json.dumps(
                    xmltodict.parse(fd.read(), attr_prefix="", dict_constructor=dict)
                )
            )
            self.json_data = content[ROOT][APPLICATION][WINDOW]

    @staticmethod
    def cleanup_object(obj):
        """Remove all sub-elements from an object."""
        return {k: v for k, v in obj.items() if XCUI_PREFIX not in k}

    @staticmethod
    def all_conditions(element, conditions):
        """Check if element matches all conditions."""
        matched = []
        for k, v in conditions.items():
            if isinstance(v, list):
                matched.append(element.get(k) in v)
            else:
                matched.append(element.get(k) == v)
        return all(matched)

    def add_leaf(self, leaves, subitems):
        """Add subvalue for each leaf."""
        if isinstance(leaves, list):
            for leaf in leaves:
                self.add_leaf(leaf, subitems)
        else:
            subitems.append([v for k, v in leaves.items() if XCUI_PREFIX in k])

    def find_subelement(self, leaves):
        if not leaves:
            return
        subitems = []
        self.add_leaf(leaves, subitems)
        return subitems

    def add_matched_element(self, element, conditions, result):
        """Add all elements which matches by all conditions."""
        if isinstance(element, list):
            for el in element:
                self.add_matched_element(el, conditions, result)
        else:
            if self.all_conditions(element, conditions):
                result.append(self.cleanup_object(element))

    def check_matches(self, element, conditions, result):
        if not element:
            return
        self.add_matched_element(element, conditions, result)

    def get_data(self, **kwargs):
        result = []
        for element in self.json_data:
            self.check_matches(element, kwargs, result)
            sublement = self.find_subelement(element)
            while sublement:
                # Read all sub-elements.
                self.check_matches(sublement, kwargs, result)
                sublement = self.find_subelement(sublement)
        return result


if __name__ == '__main__':
    from pprint import pprint
    xml_to_json = XmlToJson('source_xml.xml')
    sathees_vidyo = xml_to_json.get_data(label="Sathees Vidyo")
    ibooks = xml_to_json.get_data(
        type=["XCUIElementTypeTable", "XCUIElementTypeStaticText"],
        label="iBooks"
    )

    for r in ibooks:
        pprint(r)