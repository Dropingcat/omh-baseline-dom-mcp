from mockup.dom_contract import validate

def test_aggregated_rejection():
    errors = validate({'items': [{'local_id':'x','content_type':'quote'}, {'local_id':'y','content_type':'formula'}]})
    assert len(errors) >= 8
    assert {'x','y'} <= {e['local_id'] for e in errors}
    assert all(set(e) == {'local_id','path','code','required','fix'} for e in errors)
