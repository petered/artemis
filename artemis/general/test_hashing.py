from artemis.general.hashing import compute_fixed_hash, fixed_hash_eq
import numpy as np
import sys

_IS_PYTHON_3 = sys.version_info > (3, 0)


def test_compute_fixed_hash():
    # Not really sure why the fixed hash differes between ui_code 2 and 4 here (maybe something do do with changes to strings)

    complex_obj = [1, 'd', {'a': 4, 'b': np.arange(10)}, (7, list(range(10)))]
    original_code = compute_fixed_hash(complex_obj)

    expected_code = '7EZI6UBWRWA4UTXHY6EQRDPZUI' if _IS_PYTHON_3 else '6c98fabc301361863f321f6149a8a12a'

    assert compute_fixed_hash(complex_obj) == original_code == expected_code
    complex_obj[2]['b'][6]=0

    expected_code = 'HY7ISWCVGUFJYKONSRAQ6CEXEU' if _IS_PYTHON_3 else '8aee1f739fc9a612ed72e14682026627'
    assert compute_fixed_hash(complex_obj) == expected_code != original_code
    complex_obj[2]['b'][6]=6  # Revert to old value
    assert compute_fixed_hash(complex_obj) == original_code

    x = [a for a in np.array([1, 2, 3])]  # Numpy scalars previously caused a problem
    compute_fixed_hash(x, try_objects=True)


def test_compute_fixed_hash_terminates():

    a = []
    b = [a]
    a.append(b)
    code = compute_fixed_hash(a)
    assert code == 'Z75O4QSKMLGRRE4CLJMBDQ2LRU'

    c = []
    d = [c]
    c.append(d)
    code = compute_fixed_hash(c)
    assert code == 'Z75O4QSKMLGRRE4CLJMBDQ2LRU'


def test_fixed_hash_eq():

    obj1 = [1, 'd', {'a': 4, 'b': np.arange(10)}, (7, [1, 2, 3, 4, 5])]
    obj2 = [1, 'd', {'a': 4, 'b': np.arange(10)}, (7, [1, 2, 3, 4, 5])]
    obj3 = [1, 'd', {'a': 4, 'b': np.arange(10)}, (7, [1, 2, 3, 4, 5])]
    obj3[2]['b'][4] = 0
    assert fixed_hash_eq(obj1, obj2)
    assert not fixed_hash_eq(obj1, obj3)


if __name__ == '__main__':
    test_compute_fixed_hash()
    test_compute_fixed_hash_terminates()
    test_fixed_hash_eq()