from unittest.mock import patch, MagicMock

import view

test_json = '{"book": { "title": "The Art of Testing", "isbn":"123445678"}}'


@patch('view.View.show')
def test_ownbookview_new_message(mock_view_show: MagicMock):
    ownview = view.OwnBookView()
    ownview.show(user_id='test', payload=test_json)
    mock_view_show.assert_called_once_with('test', alt_message='"The Art of Testing" marked as yours')


@patch('view.View.show')
def test_ownbookview_existing_behavior(mock_view_show: MagicMock):
    ownview = view.OwnBookView()
    assert 'Ok!' == ownview.message
    ownview.show(user_id='test', payload="{}")
    mock_view_show.assert_called_once_with('test')
