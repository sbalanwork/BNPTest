# System imports
import pytest
import logging
import xml.etree.ElementTree as ET
import pandas as pd

# Local imports
from . import processor

logger = logging.getLogger(__name__)


def test_validate_xml_invalid_input():
    xml = '<Trades><Trade CorrelationId="234" NumberOfTrades="3" Limit="1000" TradeID="654">100</Trade>'
    with pytest.raises(SystemExit):
        processor.validate_xml(xml)


def test_validate_xml_valid_input():
    xml = '<Trades><Trade CorrelationId="234" NumberOfTrades="3" Limit="1000" TradeID="654">100</Trade></Trades>'
    exp_output = ET.fromstring(xml)
    act_output = processor.validate_xml(xml)
    assert isinstance(act_output, type(exp_output))


def test_get_trade_list_from_xml_invalid():
    xml = '<Trades><Trade CorrelationId="234" NumberOfTrades="3.1" Limit="1000" TradeID="654">100</Trade></Trades>'
    root = ET.fromstring(xml)
    with pytest.raises(SystemExit):
        processor.get_trade_list_from_xml(root)


def test_get_trade_list_from_xml_valid():
    xml = '<trades><trade correlationid="234" numberoftrades="3" limit="1000" tradeid="654">100</trade></trades>'
    root = ET.fromstring(xml)
    act_output = processor.get_trade_list_from_xml(root)
    exp_output = [{"CorrelationId": "234", "NumberOfTrades": 3,
                   "Limit": 1000.0, "TradeID": "654",
                   "Amount": 100.0}]
    assert exp_output == act_output


def test_get_data_frame_from_trade_list():
    t_list = [{"CorrelationId": "234", "NumberOfTrades": 3,
                   "Limit": 1000.0, "TradeID": "654",
                   "Amount": 100.0},
              {"CorrelationId": "234", "NumberOfTrades": 3,
               "Limit": 1000.0, "TradeID": "135",
               "Amount": 200.0}
              ]
    df = pd.DataFrame(t_list)
    df.set_index('TradeID', drop=True, inplace=True)
    act_output = processor.get_data_frame_from_list(t_list)
    pd.testing.assert_frame_equal(act_output, df)


def test_process_data_frame():
    df = pd.DataFrame([
        ['1', 3, 1000, 100]
        , ['1', 3, 1000, 200]
        , ['2', 1, 500, 600]
        , ['1', 3, 1000, 200]
        , ['3', 2, 1000, 1000]
    ], columns=['CorrelationId', 'NumberOfTrades', 'Limit', 'Amount']
    )
    exp_output = "CorrelationId,NumberOfTrades,State\r\n1,3,Accepted\r\n2,1,Rejected\r\n3,1,Pending\r\n"
    act_output = processor.process_data_frame(df)
    assert exp_output == act_output
