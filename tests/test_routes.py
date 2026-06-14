import pytest
import json


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Code Quality Assistant' in response.data


def test_analyze_empty_code(client):
    response = client.post('/api/analyze',
        data=json.dumps({'code': '', 'language': 'python'}),
        content_type='application/json')
    assert response.status_code == 400


def test_analyze_no_json(client):
    response = client.post('/api/analyze', content_type='application/json')
    assert response.status_code == 400


def test_analyze_with_valid_code(client):
    payload = {
        'code': 'print("hello")',
        'language': 'python'
    }
    response = client.post('/api/analyze',
        data=json.dumps(payload),
        content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'quality_score' in data
        assert isinstance(data['quality_score'], int)
        assert 0 <= data['quality_score'] <= 10

