import sys, os, pytest
from numpy import isclose
import molgrid

sys.path.insert(0, '.')
from liGAN.molecules import read_ob_mols_from_file
from liGAN.atom_types import (
    make_one_hot, UNK, AtomTyper, Atom, ob
)


def test_make_one_hot():

    assert make_one_hot(0, []) == []
    assert make_one_hot(0, [UNK]) == [1]

    assert make_one_hot(0, [1]) == [0]
    assert make_one_hot(1, [1]) == [1]
    assert make_one_hot(0, [1, UNK]) == [0, 1]
    assert make_one_hot(1, [1, UNK]) == [1, 0]

    assert make_one_hot(0, [0, 1]) == [1, 0]
    assert make_one_hot(1, [0, 1]) == [0, 1]
    assert make_one_hot(2, [0, 1]) == [0, 0]
    assert make_one_hot(0, [0, 1, UNK]) == [1, 0, 0]
    assert make_one_hot(1, [0, 1, UNK]) == [0, 1, 0]
    assert make_one_hot(2, [0, 1, UNK]) == [0, 0, 1]


class TestUnknown(object):

    def test_eq(self):
        assert 0 == UNK
        assert 1 == UNK
        assert False == UNK
        assert True == UNK
        assert 'a' == UNK

    def test_in(self):
        assert 0 in [UNK]
        assert 1 in [UNK]
        assert False in [UNK]
        assert True in [UNK]
        assert 'a' in [UNK]

    def test_idx(self):
        assert [UNK].index(0) == 0
        assert [UNK].index(1) == 0
        assert [UNK].index(False) == 0
        assert [UNK].index(True) == 0
        assert [UNK].index('a') == 0


class TestAtomTyper(object):

    @pytest.fixture
    def typer(self):
        return AtomTyper(
            type_funcs=[
                Atom.atomic_num,
                Atom.aromatic,
                Atom.h_acceptor,
                Atom.h_donor,
            ],
            type_ranges=[
                [5, 6, 7, 8, 9, 15, 16, 17, 35, 53],
                [1],
                [1],
                [1],
            ],
            radius_func=lambda x: 1
        )

    @pytest.fixture
    def benzene(self):
        sdf_file = os.path.join(
            os.environ['LIGAN_ROOT'], 'data', 'benzene.sdf'
        )
        return read_ob_mols_from_file(sdf_file, 'sdf')[0]

    def test_typer_init(self, typer):
        assert len(typer.type_funcs) == 4
        assert len(typer.type_ranges) == 4
        assert typer.n_types == 13

    def test_typer_names(self, typer):
        print(list(typer.get_type_names()))

    def test_typer_benzene_type_vec(self, typer, benzene):
        for i, atom in enumerate(ob.OBMolAtomIter(benzene)):
            if i < 6: # aromatic carbon
                assert typer.get_type_vector(atom) == [
                    0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                    1, 0, 0,
                ]
            else: # non-polar hydrogen
                assert typer.get_type_vector(atom) == [
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0,
                ]

    def test_typer_ex_provider(self, typer):
        data_root = os.path.join(
            os.environ['LIGAN_ROOT'], 'data'
        )
        data_file = os.path.join(data_root, 'benzene.types')
        ex_provider = molgrid.ExampleProvider(
            typer, typer,
            data_root=data_root,
        )
        ex_provider.populate(data_file)
        ex = ex_provider.next_batch(1)[0]
        type_vecs = ex.coord_sets[1].type_vector
        for i, type_vec in enumerate(type_vecs):
            if i < 6: # aromatic carbon
                assert list(type_vec) == [
                    0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                    1, 0, 0,
                ]
            else: # non-polar hydrogen
                assert list(type_vec) == [
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0,
                ]
