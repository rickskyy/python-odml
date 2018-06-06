import random
import uuid
from abc import ABC, abstractmethod

import odml

RANDOM_MAX = 10000000
MAX_VALUE_LIST_NUMBER = 5
MAX_PROPERTY_LIST_NUMBER = 6
MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL = 2
MIN_NUMBER_OF_CHILDREN = 2  # number of children for the entity until there are available children left


# TODO document constants


def random_list_elem(list_obj):
    return random.choice(list_obj)


def first_list_elem(list_obj):
    return list_obj[0]


def crete_string_value(key):
    return key + '-' + str(random.randint(0, RANDOM_MAX))


def create_string_values_list(key):
    return [key + '-' + str(random.randint(0, RANDOM_MAX)) for _ in range(random.randint(0, MAX_VALUE_LIST_NUMBER))]


def create_int_value():
    return random.randint(0, RANDOM_MAX)


def create_random_date():
    year = random.randint(1950, 2010)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return "{y}-{m}-{d}".format(y=year, m=month, d=day)


def create_int_values_list():
    return [random.randint(0, RANDOM_MAX) for _ in range(random.randint(0, MAX_VALUE_LIST_NUMBER))]


def generate_entity_list(entity, gen_func, n, entity_list=None):
    if entity_list is None:
        entity_list = []
    for _ in range(n):
        entity_list.append(gen_func(entity))

    return entity_list


class OdmlEntityExamples(ABC):

    @abstractmethod
    def create_from_samples(self, **kwargs):
        pass

    @abstractmethod
    def create_random_from_samples(self, **kwargs):
        pass

    @abstractmethod
    def create_random(self):
        pass

    def fill_kwargs(self, obj, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key in obj:
                    obj[key] = value

    def _get_obj_dict(self, example, decision_function=random_list_elem):
        return_obj = {}

        for key, value in example.obj.items():
            return_obj[key] = decision_function(value)

        return_obj['oid'] = str(uuid.uuid4())

        return return_obj

    def _get_full_random_obj_dict(self, example):
        return_obj = {}

        for key, value in example.obj.items():
            if key == 'value':
                pass
            elif key == 'date':
                return_obj[key] = create_random_date()
            elif isinstance(example, PropertyExample) and example.obj['dtype'][0] == 'int':
                return_obj['dtype'] = 'int'
                return_obj['value'] = create_int_values_list()
            elif isinstance(example, PropertyExample) and example.obj['dtype'][0] == 'string':
                return_obj['dtype'] = 'string'
                return_obj['value'] = create_string_values_list('val')
            else:
                return_obj[key] = crete_string_value(key)

        return_obj['oid'] = str(uuid.uuid4())

        return return_obj


class DocExample(OdmlEntityExamples):

    def __init__(self, **kwargs):
        self.obj = {
            'version': ['1.0', '1.1', '1.2'],
            'author': ['Prof Jones', 'Dr Mc Gregory'],
            'date': ['2000-01-01', '2000-02-02'],
            'repository': ['rep1', 'rep2'],
        }

        self.fill_kwargs(self.obj, **kwargs)

    def create_from_samples(self, **kwargs):
        return odml.Document(**self._get_obj_dict(self, first_list_elem))

    def create_random_from_samples(self, **kwargs):
        return odml.Document(**self._get_obj_dict(self, random_list_elem))

    def create_random(self):
        return odml.Document(**self._get_full_random_obj_dict(self))


class SectionExample(OdmlEntityExamples):

    def __init__(self, **kwargs):
        self.obj = {
            'type': ['hardware', 'settings', 'DataAcquisition'],
            'name': ['exp-details1', 'exp-details2', 'exp-details3'],
            'definition': ['def1', 'def2'],
            'repository': ['rep1', 'rep2'],
        }

        self.fill_kwargs(self.obj, **kwargs)

    def create_from_samples(self, **kwargs):
        return odml.Section(**self._get_obj_dict(self, first_list_elem))

    def create_random_from_samples(self, **kwargs):
        return odml.Section(**self._get_obj_dict(self, random_list_elem))

    def create_random(self):
        s = odml.Section(**self._get_full_random_obj_dict(self))
        # need this because there is no way to specify property field in constructor
        generate_entity_list(PropertyExample(),
                             PropertyExample.create_random,
                             random.randint(1, MAX_PROPERTY_LIST_NUMBER),
                             entity_list=s)
        return s


class PropertyExample(OdmlEntityExamples):

    def __init__(self, **kwargs):
        self.obj = {
            'name': [],
            'unit': [],
            'definition': [],
            'dtype': [random.choice(('string', 'int'))],  # randomly choosing of a new property
            'value': {'string': [], 'int': []}
        }

        self.fill_kwargs(self.obj, **kwargs)

    def create_from_samples(self, **kwargs):
        """
        :param kwargs:
            random: True or False
            prop_type: 'string' or 'int'
        :return:
        """
        raise NotImplementedError("In method " + self.create_from_samples.__name__)

    def create_random_from_samples(self, **kwargs):
        raise NotImplementedError("In method " + self.create_random_from_samples.__name__)

    def create_random(self):
        return odml.Property(**self._get_full_random_obj_dict(self))


class OdmlFilesGenerator:

    def __init__(self):
        self.width = None
        self.height = None
        self.randomness = None
        self.number_entities = None
        self.max_sec_sec_children = None
        self.max_sec_prop_children = None
        self.tree = []

    def to_rdf(self):
        pass

    def _add_sections(self):
        pass

    def _add_properties(self):
        pass

    def _create_empty_tree(self, height):
        self.tree = [[] * height]

    def _merge_entities(self, tree):
        if len(tree) == 1:
            return tree

        for lindex in range(1, len(tree)):
            # parents less than children
            #  TODO move to another function condition below
            if len(tree[lindex - 1]) < len(tree[lindex]):
                children_n = int(len(tree[lindex]) / len(tree[lindex - 1]))
                if children_n < MIN_NUMBER_OF_CHILDREN:
                    children_n = MIN_NUMBER_OF_CHILDREN
                i = 0
                parent = tree[lindex - 1][i]
                for eindex in range(len(tree[lindex])):  # iterating through children
                    parent.append(tree[lindex][eindex])
                    # making parents have equal number of children, last have the rest
                    if (eindex + 1) % children_n == 0 and i + 1 < len(tree[lindex - 1]):
                        i += 1
                        parent = tree[lindex - 1][i]
            else:  # parents more or equal number comparing to children
                i = 0
                parent = tree[lindex - 1][i]
                for eindex in range(len(tree[lindex])):  # iterating through children
                    parent.append(tree[lindex][eindex])
                    if (eindex + 1) % MIN_NUMBER_OF_CHILDREN == 0 and i + 1 < len(tree[lindex - 1]):
                        i += 1
                        parent = tree[lindex - 1][i]

        return tree

    def merge_rdf_files(self):
        """
        Create one big graph from multiple rdf files. Merges without serializing rdf files
        :return:
        """
        pass

    def generate(self, width, height, randomness, number_entities,
                 max_min_sec_sec_children=(10, 2), max_min_sec_prop_children=(10, 1),
                 from_samples=False, random_number_of_children=False):
        self.width = width
        self.height = height
        self.randomness = randomness
        self.number_entities = number_entities
        self.max_sec_sec_children = max_min_sec_sec_children
        self.max_sec_prop_children = max_min_sec_prop_children

    def generate_by_width_height_entitiesnumber(self, width, height, randomness, number_entities):
        self.width = width
        self.height = height
        self.randomness = randomness
        self.number_entities = number_entities

        # self._create_empty_tree(height)

        if number_entities < width:
            #  TODO return one level
            pass

        entities_left = number_entities - width  # nodes left to build a tree
        levels_left = height - 1  # number of levels to fill,
        # maximum of nodes on the current level depending of levels_left and entities_left
        # maybe introduce better system - bias to create more like tree structure (top level < bottom)
        level_max = int(entities_left / levels_left)
        if level_max < MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL:
            level_max = MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL

        while levels_left > 0:

            current_level_n = random.randint(MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL, level_max)
            if current_level_n > width:
                current_level_n = width

            self.tree.append(generate_entity_list(SectionExample(), SectionExample.create_random, current_level_n))

            entities_left -= current_level_n
            level_max = int(entities_left / levels_left)
            levels_left -= 1

            if level_max < MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL:
                level_max = MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL

            if entities_left < MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL:
                break

        if entities_left > width:
            self.tree.append(generate_entity_list(SectionExample(), SectionExample.create_random, width))
        elif entities_left > MIN_NUMBER_OF_ENTITIES_ON_THE_LEVEL:
            self.tree.append(generate_entity_list(SectionExample(), SectionExample.create_random, entities_left))

        # append max level, might be any level
        self.tree.append(generate_entity_list(SectionExample(), SectionExample.create_random, width))

        self.tree = self._merge_entities(self.tree)

        doc = DocExample().create_random()
        for s in self.tree[0]:
            doc.append(s)

        return doc

    def generate_by_width_children(self, width, randomness,
                                   max_min_sec_sec_children=(10, 2), max_min_sec_prop_children=(10, 1)):
        self.max_sec_sec_children = max_min_sec_sec_children
        self.max_sec_prop_children = max_min_sec_prop_children
        self.randomness = randomness
        self.width = width

    def generate_by_width_height(self):
        pass

    def generate_by_height_entitiesnumber(self):
        pass

    def testg(self):
        # a = self._generate_entity_list(SectionExample(), SectionExample.create_random, 10)
        # print(a)
        import time
        c = time.time()
        doc = self.generate_by_width_height_entitiesnumber(width=10, height=6, number_entities=30, randomness=None)
        print(time.time() - c)

        import pprint
        pprint.pprint(doc)


OdmlFilesGenerator().testg()

