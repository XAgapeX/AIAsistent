import pytest
from app.services.gemini_service import normalize_quality_score, remove_comments_from_code


def test_normalize_quality_score_valid():
    data = {'quality_score': 5}
    result = normalize_quality_score(data)
    assert result['quality_score'] == 5


def test_normalize_quality_score_above_max():
    data = {'quality_score': 15}
    result = normalize_quality_score(data)
    assert result['quality_score'] == 10


def test_normalize_quality_score_below_min():
    data = {'quality_score': -5}
    result = normalize_quality_score(data)
    assert result['quality_score'] == 0


def test_normalize_quality_score_float():
    data = {'quality_score': 7.8}
    result = normalize_quality_score(data)
    assert result['quality_score'] == 7


def test_remove_comments_python():
    data = {
        'corrected_code': 'x = 5  # this is a comment\nprint(x)  # output'
    }
    result = remove_comments_from_code(data)
    assert '#' not in result['corrected_code']
    assert 'x = 5' in result['corrected_code']
    assert 'print(x)' in result['corrected_code']


def test_remove_comments_full_line():
    data = {
        'corrected_code': '# comment line\nx = 5\n# another comment\nprint(x)'
    }
    result = remove_comments_from_code(data)
    assert '# comment line' not in result['corrected_code']
    assert 'x = 5' in result['corrected_code']


def test_remove_comments_preserves_string():
    data = {
        'corrected_code': 'message = "hello # world"\nprint(message)  # print it'
    }
    result = remove_comments_from_code(data)
    assert 'hello # world' in result['corrected_code']


def test_normalize_missing_corrected_code():
    data = {'quality_score': 5}
    result = normalize_quality_score(data)
    assert 'corrected_code' in result
    assert result['corrected_code'] == ''

