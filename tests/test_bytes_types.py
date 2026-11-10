import copy
import pytest
from mockup.dom_contract import validate,strict_loads,canonical,digest,normalized,decode,raw_hash
from mockup.fixtures import package,item

@pytest.mark.parametrize('typ', ['quote','decision','formula','code','data','concept','text'])
def test_seven_types_and_required_metadata(typ):
    p=package(items=[item(typ=typ)])
    assert validate(p)==[]
    m=p['items'][0]['metadata']; m.pop(next(iter(m)))
    assert validate(p)

@pytest.mark.parametrize('text',['{"x":1,"x":2}','{"x":1.0}','{"x":NaN}','{"x":"\\ud800"}','{"x":9007199254740992}'])
def test_restricted_json(text):
    with pytest.raises(ValueError): strict_loads(text)

def test_reorder_set_arrays_not_ordered():
    p=package(items=[item('z'),item('a')]); p['items'][0]['metadata']['alternatives']=['a','b']
    q=copy.deepcopy(p); q['items'].reverse()
    assert digest(normalized(p,'a','r'))==digest(normalized(q,'a','r'))
    q['items'][1]['metadata']['alternatives'].reverse()
    assert digest(normalized(p,'a','r'))!=digest(normalized(q,'a','r'))
    q=copy.deepcopy(p); q['expected_branch_revision']=True
    assert any(e['code']=='INVALID_TYPE' for e in validate(q))

def test_golden_raw_vectors():
    """Self-contained golden vectors: no dependency on ``research/``.

    The expected digests are literals recomputed independently with
    ``hashlib.sha256`` in the same test, so the check does not trust the
    implementation under test and the suite stays hermetic.
    """
    import hashlib
    vectors = [
        ('lf', '410a', '06f961b802bc46ee168555f066d28f4f0e9afdf3f88174c1ee6f9de004fc30a0'),
        ('crlf', '410d0a', '26ffd5886253906a36a7ea0f6e26056fc36472626cb4894bcb100a34dc69d1db'),
        ('space', '41200a', '176e57a293afe5b69b551c025c0af48ee499ae79107ce376186d98b362697f6c'),
        ('unicode_nfc', 'c3a9', '4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c'),
        ('unicode_nfd', '65cc81', 'bf12767b0f2a56b2190075bae8169f656e3ce8d6357d4aff184bc6c7ea48f9f6'),
        ('decimal', '312e32333030652d3430206d6f6c2f4c', '71deb40e2a218f2ad344c29dd0d28d1ff4a79fcd464b5b9c2d6ae6c46d082ee4'),
    ]
    for name, hex_bytes, expected in vectors:
        raw = bytes.fromhex(hex_bytes)
        assert hashlib.sha256(raw).hexdigest() == expected, name
        assert raw_hash(raw) == expected, name
        assert decode(item(raw=raw)['body_b64']) == raw, name
    # every vector stays byte-distinct: no normalization anywhere in the path
    assert len({expected for _, _, expected in vectors}) == len(vectors)
    assert canonical({'b': '😀', 'a': 'e\u0301'}) == b'{"a":"e\\u0301","b":"\\ud83d\\ude00"}'
