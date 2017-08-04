import logging as log

from collections import defaultdict

from models.fixture import Fixture
from util.jsonloader import JSONLoader

class FixtureIdError(Exception):
    def __init__(self, msg, strand, address):
        super(FixtureIdError, self).__init__(
            "%s: [%d:%d]" % (msg, strand, address)
        )

class Scene(JSONLoader):

    def __init__(self, filename=None):
        JSONLoader.__init__(self, filename)
        self._dirty = False
        self._fixtures = None
        self._fixture_hierarchy = None
        # The model really shouldn't contain a reference to its controller, but
        # this makes the current refactor easier
        self._controller = None

    def set_controller(self, controller):
        assert self._controller is None
        self._controller = controller
        self._hydrate()

    def _hydrate(self):
        assert self._controller is not None
        assert self._fixtures is None
        assert self._fixture_hierarchy is None

        if self._data.get("fixtures", None):
            self._fixtures = [Fixture(data=fd, controller=self._controller)
                              for fd in self._data["fixtures"]]
        else:
            self._fixtures = []

        self._fixture_hierarchy = defaultdict(dict)
        for f in self._fixtures:
            self._fixture_hierarchy[f.strand()][f.address()] = f


    def save(self):
        if self._dirty:
            self._data["fixtures"] = [f.pack() for f in self._fixtures]

        JSONLoader.save(self)

    def extents(self):
        return tuple(self._data.get("extents", (100, 100)))

    def bounding_box(self):
        return tuple(self._data.get("bounding-box", self.extents()))

    def center(self):
        return tuple(self._data.get("center", (50, 50)))

    def set_center(self, point):
        self._data["center"] = point

    def name(self):
        return self._data.get("name", "")

    def fixtures(self):
        return self._fixtures

    def fixture(self, strand, address):
        if (strand in self._fixture_hierarchy
            and address in self._fixture_hierarchy[strand]):
            return self._fixture_hierarchy[strand][address]
        return None

    def add_fixture(self, fixture):
        assert fixture not in self._fixtures
        if (fixture.strand() in self._fixture_hierarchy
            and fixture.address() in self._fixture_hierarchy[fixture.strand()]):
            raise FixtureIdError("Attempt to add a fixture with "
                                 "strand/address that already exists",
                                 fixture.strand(), fixture.address())

        self._fixtures.append(fixture)
        self._fixture_hierarchy[fixture.strand()][fixture.address()] = fixture
        self._dirty = True

    def delete_fixture(self, fixture):
        assert fixture in self._fixtures
        self._fixtures.remove(fixture)
        del self._fixture_hierarchy[fixture.strand()][fixture.address()]
        if not self._fixture_hierarchy[fixture.strand()]:
            del self._fixture_hierarchy[fixture.strand()]
        fixture.destroy()
        self._dirty = True

    def clear_fixtures(self):
        for fixture in self._fixtures:
            fixture.destroy()
        self._fixtures = []
        self._fixture_hierarchy = defaultdict(dict)
        self._dirty = True

    def update_fixture(self, fixture, new_strand, new_address):
        assert fixture in self._fixtures
        if (new_strand in self._fixture_hierarchy
            and new_address in self._fixture_hierarchy[new_strand]):
            raise FixtureIdError("Attempt to use an existing strand/address",
                                 new_strand, new_address)

        old_strand = fixture.strand()
        old_address = fixture.address()
        del self._fixture_hierarchy[old_strand][old_address]
        if not self._fixture_hierarchy[old_strand]:
            del self._fixture_hierarchy[old_strand]
        fixture.set_strand(new_strand)
        fixture.set_address(new_address)
        self._fixture_hierarchy[new_strand][new_address] = fixture
        self._dirty = True

    def fixture_hierarchy(self):
        return self._fixture_hierarchy
